#!/usr/bin/env bun
/**
 * Facebook 自動發文腳本
 * 使用 Chrome DevTools Protocol 實現自動化
 */

import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import { mkdir } from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';

// Facebook URL
const FB_HOME_URL = 'https://www.facebook.com/';

function getScriptDir(): string {
  return path.dirname(new URL(import.meta.url).pathname);
}

function getProfileDir(): string {
  const base = process.env.FB_BROWSER_PROFILE_DIR ||
    (process.platform === 'darwin'
      ? path.join(os.homedir(), 'Library', 'Application Support', 'fb-browser-profile')
      : process.platform === 'win32'
        ? path.join(process.env.APPDATA || os.homedir(), 'fb-browser-profile')
        : path.join(os.homedir(), '.local', 'share', 'fb-browser-profile'));
  return base;
}

function findChrome(): string | undefined {
  const override = process.env.FB_BROWSER_CHROME_PATH?.trim();
  if (override && fs.existsSync(override)) return override;

  const candidates: string[] = [];
  switch (process.platform) {
    case 'darwin':
      candidates.push(
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
        '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
      );
      break;
    case 'win32':
      candidates.push(
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
      );
      break;
    default:
      candidates.push(
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/microsoft-edge',
      );
      break;
  }

  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  return undefined;
}

async function getFreePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      if (!address || typeof address === 'string') {
        server.close(() => reject(new Error('無法取得空閒 port')));
        return;
      }
      const port = address.port;
      server.close((err) => {
        if (err) reject(err);
        else resolve(port);
      });
    });
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForChromeDebugPort(port: number, timeoutMs: number): Promise<string> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (res.ok) {
        const data = await res.json() as { webSocketDebuggerUrl?: string };
        if (data.webSocketDebuggerUrl) return data.webSocketDebuggerUrl;
      }
    } catch {}
    await sleep(200);
  }
  throw new Error('Chrome debug port 連線超時');
}

// 簡單 CDP 連線類別
class CdpConnection {
  private ws: WebSocket;
  private nextId = 0;
  private pending = new Map<number, { resolve: (v: any) => void; reject: (e: Error) => void }>();

  private constructor(ws: WebSocket) {
    this.ws = ws;
    this.ws.addEventListener('message', (event) => {
      try {
        const data = typeof event.data === 'string' ? event.data : new TextDecoder().decode(event.data as ArrayBuffer);
        const msg = JSON.parse(data) as { id?: number; result?: unknown; error?: { message?: string } };
        if (msg.id) {
          const p = this.pending.get(msg.id);
          if (p) {
            this.pending.delete(msg.id);
            if (msg.error?.message) p.reject(new Error(msg.error.message));
            else p.resolve(msg.result);
          }
        }
      } catch {}
    });
  }

  static async connect(url: string, timeoutMs = 30000): Promise<CdpConnection> {
    const ws = new WebSocket(url);
    await new Promise<void>((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('CDP 連線超時')), timeoutMs);
      ws.addEventListener('open', () => { clearTimeout(timer); resolve(); });
      ws.addEventListener('error', () => { clearTimeout(timer); reject(new Error('CDP 連線失敗')); });
    });
    return new CdpConnection(ws);
  }

  async send<T = unknown>(method: string, params?: Record<string, unknown>, sessionId?: string): Promise<T> {
    const id = ++this.nextId;
    const message: Record<string, unknown> = { id, method };
    if (params) message.params = params;
    if (sessionId) message.sessionId = sessionId;

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`CDP 超時: ${method}`)); }, 60000);
      this.pending.set(id, {
        resolve: (v) => { clearTimeout(timer); resolve(v as T); },
        reject: (e) => { clearTimeout(timer); reject(e); }
      });
      this.ws.send(JSON.stringify(message));
    });
  }

  close(): void {
    try { this.ws.close(); } catch {}
  }
}

interface FBPostOptions {
  text?: string;
  images?: string[];
  target: 'page' | 'personal';
  pageName?: string;
  submit?: boolean;
  timeoutMs?: number;
  profileDir?: string;
}

export async function postToFB(options: FBPostOptions): Promise<void> {
  const { text, images = [], target, pageName, submit = false, timeoutMs = 120000, profileDir = getProfileDir() } = options;

  const chromePath = findChrome();
  if (!chromePath) throw new Error('找不到 Chrome。請設定 FB_BROWSER_CHROME_PATH 環境變數。');

  await mkdir(profileDir, { recursive: true });

  const port = await getFreePort();
  console.log(`[fb-browser] 啟動 Chrome (profile: ${profileDir})`);

  const startUrl = target === 'page' && pageName
    ? `https://www.facebook.com/${encodeURIComponent(pageName)}/`
    : FB_HOME_URL;

  const chrome = spawn(chromePath, [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-blink-features=AutomationControlled',
    '--start-maximized',
    startUrl,
  ], { stdio: 'ignore' });

  let cdp: CdpConnection | null = null;

  try {
    const wsUrl = await waitForChromeDebugPort(port, 30000);
    cdp = await CdpConnection.connect(wsUrl);

    // 取得頁面
    const targets = await cdp.send<{ targetInfos: Array<{ targetId: string; url: string; type: string }> }>('Target.getTargets');
    let pageTarget = targets.targetInfos.find(t => t.type === 'page' && t.url.includes('facebook.com'));

    if (!pageTarget) {
      const { targetId } = await cdp.send<{ targetId: string }>('Target.createTarget', { url: startUrl });
      pageTarget = { targetId, url: startUrl, type: 'page' };
    }

    const { sessionId } = await cdp.send<{ sessionId: string }>('Target.attachToTarget', { targetId: pageTarget.targetId, flatten: true });

    await cdp.send('Page.enable', {}, sessionId);
    await cdp.send('Runtime.enable', {}, sessionId);
    await cdp.send('DOM.enable', {}, sessionId);

    console.log('[fb-browser] 等待 Facebook 頁面載入...');
    await sleep(5000);

    // 檢查登入狀態
    const checkLogin = async (): Promise<boolean> => {
      const result = await cdp!.send<{ result: { value: boolean } }>('Runtime.evaluate', {
        expression: `
          // 檢查是否有發文區域或登入後才有的元素
          !!document.querySelector('[aria-label*="建立貼文"]') ||
          !!document.querySelector('[aria-label*="Create a post"]') ||
          !!document.querySelector('[aria-label*="發佈"]') ||
          !!document.querySelector('[data-pagelet="ProfileComposer"]') ||
          !!document.querySelector('[role="main"] [contenteditable="true"]')
        `,
        returnByValue: true,
      }, sessionId);
      return result.result.value;
    };

    let isLoggedIn = await checkLogin();
    if (!isLoggedIn) {
      console.log('[fb-browser] 請在瀏覽器中登入 Facebook...');
      const start = Date.now();
      while (Date.now() - start < timeoutMs) {
        await sleep(3000);
        isLoggedIn = await checkLogin();
        if (isLoggedIn) break;
      }
      if (!isLoggedIn) throw new Error('登入超時。請先手動登入 Facebook。');
    }

    console.log('[fb-browser] 已登入，準備發文...');

    // 點擊發文區域
    await cdp.send('Runtime.evaluate', {
      expression: `
        (function() {
          // 1. 嘗試常見的 aria-label
          let composer = document.querySelector('[aria-label*="建立貼文"]') ||
                         document.querySelector('[aria-label*="Create a post"]') ||
                         document.querySelector('[aria-label*="你在想什麼"]') ||
                         document.querySelector('[aria-label*="What\\'s on your mind"]') ||
                         document.querySelector('[data-pagelet="ProfileComposer"]');
          
          // 2. 如果沒找到，嘗試搜尋包含特定文字的按鈕 (針對用戶截圖中的「在想什麼」)
          if (!composer) {
            const buttons = Array.from(document.querySelectorAll('[role="button"], div, span'));
            composer = buttons.find(el => 
              (el.innerText && (el.innerText.includes('在想什麼') || el.innerText.includes('on your mind')))
            );
          }

          if (composer) {
            composer.click();
            return true;
          }
          return false;
        })()
      `,
    }, sessionId);

    await sleep(3000);

    // 等待編輯器出現
    const waitForEditor = async (): Promise<boolean> => {
      const start = Date.now();
      while (Date.now() - start < 30000) {
        const result = await cdp!.send<{ result: { value: boolean } }>('Runtime.evaluate', {
          expression: `
            !!document.querySelector('[contenteditable="true"][data-lexical-editor="true"]') ||
            !!document.querySelector('[contenteditable="true"][role="textbox"]') ||
            !!document.querySelector('div[contenteditable="true"]') ||
            !!document.querySelector('[aria-label*="建立貼文"] [contenteditable="true"]')
          `,
          returnByValue: true,
        }, sessionId);
        if (result.result.value) return true;
        await sleep(1000);
      }
      return false;
    };

    const editorFound = await waitForEditor();
    if (!editorFound) {
      console.log('[fb-browser] 找不到編輯器，嘗試二次重試點擊...');
      await cdp.send('Runtime.evaluate', {
        expression: `
          // 嘗試點擊包含「在想什麼」字樣的元素
          const elements = Array.from(document.querySelectorAll('*'));
          const target = elements.find(el => 
            el.children.length === 0 && 
            (el.innerText && (el.innerText.includes('在想什麼') || el.innerText.includes('on your mind')))
          );
          if (target) target.click();
        `,
      }, sessionId);
      await sleep(3000);
    }

    // 輸入文字
    if (text) {
      console.log('[fb-browser] 輸入貼文內容...');
      await cdp.send('Runtime.evaluate', {
        expression: `
          const editor = document.querySelector('[contenteditable="true"][data-lexical-editor="true"]') ||
                        document.querySelector('[contenteditable="true"][role="textbox"]') ||
                        document.querySelector('div[contenteditable="true"]');
          if (editor) {
            editor.focus();
            document.execCommand('insertText', false, ${JSON.stringify(text)});
          }
        `,
      }, sessionId);
      await sleep(1000);
    }

    // 上傳圖片
    for (const imagePath of images) {
      if (!fs.existsSync(imagePath)) {
        console.warn(`[fb-browser] 圖片不存在: ${imagePath}`);
        continue;
      }

      console.log(`[fb-browser] 上傳圖片: ${imagePath}`);

      // 嘗試找到圖片/影片按鈕並點擊
      await cdp.send('Runtime.evaluate', {
        expression: `
          (function() {
            const photoBtn = document.querySelector('[aria-label*="相片"]') ||
                            document.querySelector('[aria-label*="Photo"]') ||
                            document.querySelector('[aria-label*="圖片"]') ||
                            document.querySelector('div[role="button"][aria-label*="相片/影片"]');
            if (photoBtn) {
              photoBtn.click();
              return true;
            }
            return false;
          })()
        `,
        returnByValue: true,
      }, sessionId);

      await sleep(2000);

      // 取得絕對路徑
      const absPath = path.resolve(imagePath);

      // 使用 CDP DOM.setFileInputFiles 上傳檔案
      try {
        // 1. 取得 Document
        const { root } = await cdp.send<{ root: { nodeId: number } }>('DOM.getDocument', { depth: -1, pierce: true }, sessionId);
        
        // 2. 尋找 file input
        const { nodeId } = await cdp.send<{ nodeId: number }>('DOM.querySelector', {
          nodeId: root.nodeId,
          selector: 'input[type="file"][accept*="image"]'
        }, sessionId);

        if (nodeId) {
          // 3. 設定檔案
          await cdp.send('DOM.setFileInputFiles', {
            files: [absPath],
            nodeId: nodeId
          }, sessionId);
          console.log(`[fb-browser] 已透過 CDP 設定檔案: ${absPath}`);
        } else {
          throw new Error('找不到檔案上傳輸入框');
        }
      } catch (err) {
        console.error(`[fb-browser] CDP 上傳失敗，嘗試備用方案: ${err instanceof Error ? err.message : String(err)}`);
        // 備用方案：傳統方式（雖然可能無效，但作為最後手段）
        await cdp.send('Runtime.evaluate', {
          expression: `
            const input = document.querySelector('input[type="file"][accept*="image"]');
            if (input) input.click();
          `,
        }, sessionId);
      }

      console.log('[fb-browser] 等待圖片上傳...');
      await sleep(5000); // 給予更多時間上傳
    }

    // 發布或預覽
    if (submit) {
      console.log('[fb-browser] 發布貼文...');
      await cdp.send('Runtime.evaluate', {
        expression: `
          const postBtn = document.querySelector('[aria-label*="發佈"]') ||
                         document.querySelector('[aria-label*="Post"]') ||
                         document.querySelector('div[aria-label*="發佈"]');
          if (postBtn) postBtn.click();
        `,
      }, sessionId);
      await sleep(3000);
      console.log('[fb-browser] ✓ 貼文已發布！');
    } else {
      console.log('[fb-browser] 貼文已準備好（預覽模式）。使用 --submit 來實際發布。');
      console.log('[fb-browser] 瀏覽器將保持開啟 30 秒供預覽...');
      await sleep(30000);
    }

  } finally {
    if (cdp) {
      try { await cdp.send('Browser.close'); } catch {}
      cdp.close();
    }

    setTimeout(() => {
      if (!chrome.killed) try { chrome.kill('SIGKILL'); } catch {}
    }, 2000);
    try { chrome.kill('SIGTERM'); } catch {}
  }
}

function printUsage(): never {
  console.log(`發布內容到 Facebook

使用方式:
  npx -y bun fb-browser.ts [options] [text]

選項:
  --image <path>      新增圖片（可重複使用，最多 4 張）
  --target <type>     目標：page（粉專）或 personal（個人）
  --page-name <name>  粉專名稱（當 target=page 時必填）
  --submit            實際發布（預設為預覽模式）
  --profile <dir>     Chrome profile 目錄
  --help              顯示說明

範例:
  npx -y bun fb-browser.ts "Hello!" --target personal
  npx -y bun fb-browser.ts "Check this!" --image photo.png --target page --page-name "MyPage" --submit
`);
  process.exit(0);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) printUsage();

  const images: string[] = [];
  let submit = false;
  let profileDir: string | undefined;
  let target: 'page' | 'personal' = 'personal';
  let pageName: string | undefined;
  const textParts: string[] = [];

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg === '--image' && args[i + 1]) {
      images.push(args[++i]!);
    } else if (arg === '--submit') {
      submit = true;
    } else if (arg === '--profile' && args[i + 1]) {
      profileDir = args[++i];
    } else if (arg === '--target' && args[i + 1]) {
      const t = args[++i]!;
      if (t === 'page' || t === 'personal') target = t;
    } else if ((arg === '--page-name' || arg === '--page') && args[i + 1]) {
      pageName = args[++i];
    } else if (!arg.startsWith('-')) {
      textParts.push(arg);
    }
  }

  const text = textParts.join(' ').trim() || undefined;

  if (!text && images.length === 0) {
    console.error('錯誤：請提供貼文內容或至少一張圖片。');
    process.exit(1);
  }

  if (target === 'page' && !pageName) {
    console.error('錯誤：發布到粉專時需要指定 --page-name。');
    process.exit(1);
  }

  await postToFB({ text, images, target, pageName, submit, profileDir });
}

main().catch((err) => {
  console.error(`錯誤：${err instanceof Error ? err.message : String(err)}`);
  process.exit(1);
});

