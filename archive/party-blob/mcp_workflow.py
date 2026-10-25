"""Exercise the repository's actual stdio MCP server; retain structured evidence."""
import asyncio
import json
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PROJECT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else OUT / 'font'

async def main():
    jobs = json.loads(Path(sys.argv[1]).read_text())
    params = StdioServerParameters(command=str(ROOT / '.venv/bin/fontmaker-mcp'), cwd=ROOT)
    async with stdio_client(params) as (reader, writer), ClientSession(reader, writer) as session:
        await session.initialize()
        state = {}
        if (PROJECT / 'font.yaml').exists():
            result = await session.call_tool('open_font_project', {'path': str(PROJECT)})
            state = result.structured_content
        for job in jobs:
            name, args = job['tool'], dict(job.get('args', {}))
            if job.get('project', True) and state:
                args['project_id'] = state['project_id']
            if job.get('mutate'):
                inspected = await session.call_tool('get_font_project', {'project_id': state['project_id']})
                args['expected_revision'] = inspected.structured_content['revision']
            if name == 'upsert_glyphs' and 'glyph_file' in job:
                args['glyphs'] = json.loads((OUT / job['glyph_file']).read_text())
            result = await session.call_tool(name, args)
            data = result.structured_content
            if data is None:
                data = {'content': [x.text for x in result.content if x.type == 'text']}
            record = {'tool': name, 'arguments': args, 'result': data, 'is_error': result.is_error}
            with (OUT / 'mcp-transcript.jsonl').open('a') as f:
                f.write(json.dumps(record) + '\n')
            if job.get('save'):
                (OUT / job['save']).write_text(json.dumps(data, indent=2))
            if result.is_error or 'error' in data:
                print(json.dumps(record, indent=2)); raise RuntimeError(name)
            if 'revision' in data:
                state.update({k: data[k] for k in ('project_id', 'revision') if k in data})
            print(name, json.dumps(data if name in ('create_font_project','validate_font_project','build_font','suggest_spacing') else {k: data[k] for k in ('revision','changed','artifacts','total_advance') if k in data}), flush=True)

asyncio.run(main())
