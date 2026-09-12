import process from 'process';

function readArg(name) {
  const index = process.argv.indexOf(name);
  if (index < 0) {
    return '';
  }
  return process.argv[index + 1] || '';
}

async function main() {
  const rawMessages = readArg('--messages-json');
  if (!rawMessages) {
    process.stderr.write('NOVA QVAC ERROR: messages payload missing\n');
    process.exit(1);
    return;
  }

  let messages = [];
  try {
    messages = JSON.parse(rawMessages);
  } catch {
    process.stderr.write('NOVA QVAC ERROR: invalid messages payload\n');
    process.exit(1);
    return;
  }

  const host = process.env.QVAC_HOST || '127.0.0.1';
  const port = process.env.QVAC_PORT || '3055';
  const url = `http://${host}:${port}/generate`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });

    const data = await response.json();
    if (typeof data.result === 'string' && data.result.trim()) {
      process.stdout.write(data.result.trim() + '\n');
      return;
    }

    if (typeof data.error === 'string' && data.error.trim()) {
      process.stderr.write(`NOVA QVAC ERROR: ${data.error.trim()}\n`);
      process.exit(1);
      return;
    }

    process.stderr.write('NOVA QVAC ERROR: empty response\n');
    process.exit(1);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`NOVA QVAC ERROR: ${message}\n`);
    process.exit(1);
  }
}

await main();
