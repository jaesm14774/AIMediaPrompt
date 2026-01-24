#!/usr/bin/env bun
/**
 * Gemini Web API 圖片生成腳本
 * 精簡版實作，參考 baoyu-skills 的設計
 */

import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { mkdir, writeFile } from 'fs/promises';
import os from 'os';
import net from 'net';
import { Buffer } from 'buffer';

// 資料目錄
function getDataDir(): string {
  const base = process.env.GEMINI_WEB_DATA_DIR || 
    (process.platform === 'darwin' 
      ? path.join(os.homedir(), 'Library', 'Application Support', 'gemini-image-gen')
      : path.join(os.homedir(), '.local', 'share', 'gemini-image-gen'));
  return base;
}

function getCookiePath(): string {
  return process.env.GEMINI_WEB_COOKIE_PATH || path.join(getDataDir(), 'cookies.json');
}

function getProfileDir(): string {
  return process.env.GEMINI_WEB_CHROME_PROFILE_DIR || path.join(getDataDir(), 'chrome-profile');
}

// Chrome 路徑
function findChrome(): string | undefined {
  const override = process.env.GEMINI_WEB_CHROME_PATH?.trim();
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

// 取得空閒 port
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

// 等待 Chrome debug port
async function waitForChrome(port: number, timeoutMs: number): Promise<string> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (res.ok) {
        const data = await res.json() as { webSocketDebuggerUrl?: string };
        if (data.webSocketDebuggerUrl) return data.webSocketDebuggerUrl;
      }
    } catch {}
    await new Promise(r => setTimeout(r, 200));
  }
  throw new Error('Chrome debug port 連線超時');
}

// 簡單的 CDP 連線
class SimpleCDP {
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

  static async connect(url: string, timeoutMs = 30000): Promise<SimpleCDP> {
    const ws = new WebSocket(url);
    await new Promise<void>((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('CDP 連線超時')), timeoutMs);
      ws.addEventListener('open', () => { clearTimeout(timer); resolve(); });
      ws.addEventListener('error', () => { clearTimeout(timer); reject(new Error('CDP 連線失敗')); });
    });
    return new SimpleCDP(ws);
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

// 主要功能：使用 Gemini 生成圖片
async function generateWithGemini(prompt: string, outputPath: string): Promise<string> {
  const chromePath = findChrome();
  if (!chromePath) throw new Error('找不到 Chrome。請設定 GEMINI_WEB_CHROME_PATH 環境變數。');

  const profileDir = getProfileDir();
  await mkdir(profileDir, { recursive: true });

  const port = await getFreePort();
  console.log(`[generate-image] 啟動 Chrome (profile: ${profileDir})`);

  const GEMINI_URL = 'https://gemini.google.com/app';
  
  const chrome = spawn(chromePath, [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-blink-features=AutomationControlled',
    GEMINI_URL,
  ], { stdio: 'ignore' });

  let cdp: SimpleCDP | null = null;

  try {
    const wsUrl = await waitForChrome(port, 30000);
    cdp = await SimpleCDP.connect(wsUrl);

    // 取得頁面
    const targets = await cdp.send<{ targetInfos: Array<{ targetId: string; url: string; type: string }> }>('Target.getTargets');
    let pageTarget = targets.targetInfos.find(t => t.type === 'page' && t.url.includes('gemini.google.com'));

    if (!pageTarget) {
      const { targetId } = await cdp.send<{ targetId: string }>('Target.createTarget', { url: GEMINI_URL });
      pageTarget = { targetId, url: GEMINI_URL, type: 'page' };
    }

    const { sessionId } = await cdp.send<{ sessionId: string }>('Target.attachToTarget', { targetId: pageTarget.targetId, flatten: true });

    await cdp.send('Page.enable', {}, sessionId);
    await cdp.send('Runtime.enable', {}, sessionId);
    await cdp.send('DOM.enable', {}, sessionId);

    console.log('[generate-image] 等待 Gemini 頁面載入...');
    await new Promise(r => setTimeout(r, 8000)); // 增加等待時間確保頁面完全載入

    // 檢查是否需要登入 - 改進檢測邏輯
    const checkLogin = async (): Promise<boolean> => {
      const result = await cdp!.send<{ result: { value: { found: boolean } } }>('Runtime.evaluate', {
        expression: `
          (() => {
            const selectors = [
              'div[contenteditable="true"][role="textbox"]',
              'div[aria-label*="提示詞"]',
              'div[aria-label*="prompt"]',
              'textarea[placeholder*="提示詞"]',
              'textarea[placeholder*="訊息"]',
              'textarea[placeholder*="Message"]',
              '[data-placeholder*="Gemini"]'
            ];
            return {
              found: selectors.some(s => {
                const el = document.querySelector(s);
                return el && el.offsetParent !== null;
              })
            };
          })()
        `,
        returnByValue: true,
      }, sessionId);
      return result.result.value.found;
    };

    let isLoggedIn = await checkLogin();
    if (!isLoggedIn) {
      console.log('[generate-image] 請在瀏覽器中登入 Google 帳號...');
      const start = Date.now();
      while (Date.now() - start < 120000) {
        await new Promise(r => setTimeout(r, 2000));
        isLoggedIn = await checkLogin();
        if (isLoggedIn) {
          console.log('[generate-image] ✓ 登入成功，等待頁面穩定...');
          await new Promise(r => setTimeout(r, 3000));
          break;
        }
      }
      if (!isLoggedIn) throw new Error('登入超時，請重新執行。');
    }

    console.log('[generate-image] 尋找輸入框並輸入 prompt...');
    
    // 輸入 prompt
    const imagePrompt = `Generate an image: ${prompt}`;
    const inputResult = await cdp.send<{ result: { value: { success: boolean; found: boolean; selector?: string } | undefined } }>('Runtime.evaluate', {
      expression: `
        (() => {
          try {
            const selectors = [
              'div[contenteditable="true"][role="textbox"]',
              'div[aria-label*="提示詞"]',
              'div[aria-label*="prompt"]',
              'textarea[placeholder*="提示詞"]',
              'textarea[placeholder*="Message"]',
              '[data-placeholder*="Gemini"]'
            ];
            
            let textarea = null;
            let matchedSelector = '';
            for (const selector of selectors) {
              const el = document.querySelector(selector);
              if (el && el.offsetParent !== null) {
                textarea = el;
                matchedSelector = selector;
                break;
              }
            }
            
            if (textarea) {
              textarea.focus();
              const promptText = ${JSON.stringify(imagePrompt)};
              
              if (textarea.tagName === 'DIV' || textarea.contentEditable === 'true') {
                textarea.textContent = '';
                document.execCommand('insertText', false, promptText);
              } else {
                textarea.value = promptText;
              }
              
              // 觸發事件
              ['input', 'change'].forEach(type => {
                textarea.dispatchEvent(new Event(type, { bubbles: true }));
              });
              
              return { success: true, found: true, selector: matchedSelector };
            }
            return { success: false, found: false };
          } catch (e) {
            return { success: false, found: false, error: e.message };
          }
        })()
      `,
      returnByValue: true,
    }, sessionId);

    if (!inputResult.result?.value?.found) {
      throw new Error('找不到對話輸入框，請確認頁面已載入完成');
    }
    console.log(`[generate-image] ✓ Prompt 已輸入 (透過 ${inputResult.result.value.selector})`);

    await new Promise(r => setTimeout(r, 1000));

    // 送出
    const sendResult = await cdp.send<{ result: { value: boolean } }>('Runtime.evaluate', {
      expression: `
        (() => {
          const sendBtn = document.querySelector('button[aria-label*="傳送"]') || 
                         document.querySelector('button[aria-label*="Send"]') ||
                         document.querySelector('button[aria-label*="send"]') ||
                         document.querySelector('button.send-button');
          if (sendBtn && !sendBtn.disabled && sendBtn.getAttribute('aria-disabled') !== 'true') {
            sendBtn.click();
            return true;
          }
          return false;
        })()
      `,
      returnByValue: true,
    }, sessionId);

    if (!sendResult.result?.value) {
      throw new Error('找不到或無法點擊送出按鈕');
    }
    console.log('[generate-image] ✓ 已點擊送出按鈕');

    console.log('[generate-image] 等待圖片生成（可能需要 30-90 秒）...');
    
    // 等待圖片生成 - 改進檢測邏輯，排除頭像
    let imageUrl: string | null = null;
    const startGen = Date.now();
    let checkCount = 0;
    
    while (Date.now() - startGen < 180000) { // 3 分鐘
      await new Promise(r => setTimeout(r, 5000)); // 每 5 秒檢查一次
      checkCount++;
      
      if (checkCount % 6 === 0) {
        console.log(`[generate-image] 已等待 ${Math.floor((Date.now() - startGen) / 1000)} 秒...`);
      }
      
      const result = await cdp.send<{ result: { value: string | null | undefined }; exceptionDetails?: unknown }>('Runtime.evaluate', {
        expression: `
          (() => {
            try {
              // 排除頭像和圖標的選擇器
              const excludeSelectors = [
                '[role="img"][aria-label*="profile"]',
                '[role="img"][aria-label*="avatar"]',
                'img[alt*="profile"]',
                'img[alt*="avatar"]',
                'img[alt*="頭像"]',
                'img[src*="photo"]', // 通常頭像 URL 包含 photo
                'img[style*="border-radius: 50%"]', // 圓形頭像
                'img[width="32"]',
                'img[width="40"]',
                'img[width="48"]'
              ];
              
              // 排除的元素
              const excludedElements = new Set();
              excludeSelectors.forEach(selector => {
                try {
                  document.querySelectorAll(selector).forEach(el => excludedElements.add(el));
                } catch (e) {
                  // 忽略選擇器錯誤
                }
              });
              
              // 找所有圖片，但排除頭像
              const allImgs = Array.from(document.querySelectorAll('img')).filter(img => {
                try {
                  // 排除已標記的元素
                  if (excludedElements.has(img)) return false;
                  
                  const src = img.getAttribute('src') || '';
                  const alt = img.getAttribute('alt') || '';
                  const width = img.offsetWidth || img.width || 0;
                  const height = img.offsetHeight || img.height || 0;
                  
                  // 排除小圖片（可能是圖標）
                  if (width < 100 || height < 100) return false;
                  
                  // 排除明顯是頭像的 URL
                  if (src.includes('/photo') && (width < 200 || height < 200)) return false;
                  
                  // 排除 data URL（通常是小圖標）
                  if (src.startsWith('data:')) return false;
                  
                  // 排除圓形圖片（可能是頭像）
                  try {
                    const style = window.getComputedStyle(img);
                    if (style.borderRadius === '50%' && width < 200) return false;
                  } catch (e) {
                    // 忽略樣式錯誤
                  }
                  
                  // 優先選擇生成的圖片：包含特定 URL 模式
                  if (src.includes('googleusercontent') && 
                      (src.includes('/image') || src.includes('/generated') || width > 200)) {
                    return true;
                  }
                  
                  return false;
                } catch (e) {
                  return false;
                }
              });
              
              if (allImgs.length > 0) {
                // 找最大的圖片（通常是生成的圖片）
                const sortedImgs = allImgs.sort((a, b) => {
                  try {
                    const aSize = (a.offsetWidth || a.width) * (a.offsetHeight || a.height);
                    const bSize = (b.offsetWidth || b.width) * (b.offsetHeight || b.height);
                    return bSize - aSize;
                  } catch (e) {
                    return 0;
                  }
                });
                
                const targetImg = sortedImgs[0];
                const src = targetImg.getAttribute('src');
                
                // 確保是有效的 HTTP URL
                if (src && src.startsWith('http') && !src.includes('data:')) {
                  // 再次確認不是頭像（檢查父元素）
                  let parent = targetImg.parentElement;
                  let depth = 0;
                  while (parent && depth < 5) {
                    try {
                      const parentClass = parent.className || '';
                      const parentId = parent.id || '';
                      if (parentClass.includes('avatar') || 
                          parentClass.includes('profile') ||
                          parentId.includes('avatar') ||
                          parentId.includes('profile')) {
                        return null; // 可能是頭像
                      }
                    } catch (e) {
                      // 忽略錯誤
                    }
                    parent = parent.parentElement;
                    depth++;
                  }
                  
                  return src;
                }
              }
              
              return null;
            } catch (e) {
              return null;
            }
          })()
        `,
        returnByValue: true,
      }, sessionId);

      if (result.result && result.result.value && typeof result.result.value === 'string' && result.result.value.length > 0) {
        imageUrl = result.result.value;
        console.log(`[generate-image] ✓ 找到生成的圖片，準備下載...`);
        // 稍微等待一下確保圖片完全加載
        await new Promise(r => setTimeout(r, 2000));
        break;
      }
    }

    if (!imageUrl) {
      // 最後一次嘗試獲取頁面狀態
      try {
        const debugInfo = await cdp.send<{ result: { value: string | undefined }; exceptionDetails?: unknown }>('Runtime.evaluate', {
          expression: `
            (() => {
              try {
                return JSON.stringify({
                  url: window.location.href,
                  imgCount: document.querySelectorAll('img').length,
                  textareaExists: !!document.querySelector('textarea'),
                  buttons: Array.from(document.querySelectorAll('button')).map(b => b.getAttribute('aria-label')).filter(Boolean)
                });
              } catch (e) {
                return JSON.stringify({ error: e.message || String(e) });
              }
            })()
          `,
          returnByValue: true,
        }, sessionId);
        
        if (debugInfo.result && debugInfo.result.value) {
          console.error('[generate-image] 調試信息:', debugInfo.result.value);
        }
      } catch (e) {
        console.error('[generate-image] 無法獲取調試信息:', e);
      }
      
      throw new Error('圖片生成超時或失敗。請檢查瀏覽器視窗確認是否已生成圖片。');
    }

    console.log('[generate-image] 下載圖片 (使用瀏覽器截圖技術)...');
    
    // 確保圖片在視域內並取得座標，增加重試機制處理寬度為 0 的情況
    let rect = null;
    for (let i = 0; i < 10; i++) {
      const rectResult = await cdp.send<{ result: { value: any } }>('Runtime.evaluate', {
        expression: `
          (() => {
            //FIX: 使用之前已經驗證過並找到的 imageUrl，而不是依賴不可靠的 hardcoded selector
            const targetUrl = ${JSON.stringify(imageUrl)};
            
            // 搜尋所有圖片，比對 src 屬性
            const allImgs = Array.from(document.querySelectorAll('img'));
            const img = allImgs.find(el => el.src === targetUrl || el.getAttribute('src') === targetUrl);

            if (!img) return null;

            const r = img.getBoundingClientRect();
            if (r.width < 10 || r.height < 10) return { isZero: true };
            
            // 使用 instant 避免平滑捲動造成的截圖延遲
            img.scrollIntoView({ block: 'center', behavior: 'instant' });
            
            return { x: r.x, y: r.y, w: r.width, h: r.height };
          })()
        `,
        returnByValue: true,
      }, sessionId);

      const val = rectResult.result?.value;
      if (val && !val.isZero) {
        rect = val;
        break;
      }
      console.log('[generate-image] 等待圖片渲染完成...');
      await new Promise(r => setTimeout(r, 1500));
    }

    if (!rect) throw new Error('無法定位圖片或圖片尚未渲染完成');

    // 額外等待一下確保捲動和動畫停止
    await new Promise(r => setTimeout(r, 1000));

    // 直接叫瀏覽器截取該區域
    const screenshot = await cdp.send<{ data: string }>('Page.captureScreenshot', {
      format: 'png',
      clip: {
        x: Math.floor(rect.x),
        y: Math.floor(rect.y),
        width: Math.ceil(rect.w),
        height: Math.ceil(rect.h),
        scale: 1
      }
    }, sessionId);

    const buffer = Buffer.from(screenshot.data, 'base64');
    const outputDir = path.dirname(outputPath);
    await mkdir(outputDir, { recursive: true });
    await writeFile(outputPath, buffer);

    console.log(`[generate-image] ✓ 圖片已儲存：${outputPath}`);
    return outputPath;

  } catch (e) {
    throw e;
  } finally {
    if (cdp) {
      try { await cdp.send('Browser.close'); } catch {}
      cdp.close();
    }
    setTimeout(() => {
      if (!chrome.killed) try { chrome.kill('SIGKILL'); } catch {}
    }, 1000);
    try { chrome.kill('SIGTERM'); } catch {}
  }
}

// CLI
function printUsage(): void {
  console.log(`使用方式:
  npx -y bun main.ts --prompt "描述" --image output.png
  npx -y bun main.ts "描述" --image output.png

選項:
  --prompt, -p <text>   圖片描述
  --image <path>        輸出路徑（預設: generated.png）
  --help, -h            顯示說明`);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    printUsage();
    return;
  }

  let prompt: string | null = null;
  let imagePath = 'generated.png';

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg === '--prompt' || arg === '-p') {
      prompt = args[++i] ?? null;
    } else if (arg === '--image' || arg.startsWith('--image=')) {
      if (arg.startsWith('--image=')) {
        imagePath = arg.slice('--image='.length);
      } else {
        imagePath = args[++i] ?? 'generated.png';
      }
    } else if (!arg.startsWith('-') && !prompt) {
      prompt = arg;
    }
  }

  if (!prompt) {
    console.error('錯誤：請提供圖片描述');
    printUsage();
    process.exit(1);
  }

  await generateWithGemini(prompt as string, imagePath);
}

main().catch((e) => {
  console.error(`錯誤：${e instanceof Error ? e.message : String(e)}`);
  process.exit(1);
});

