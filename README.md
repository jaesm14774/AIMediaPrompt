# AIMediaPrompt

自動上傳圖片到 ImgBB 並插入 URL 到 prompt 檔案的工具。

## 功能說明

- 自動上傳 `Local_Media` 資料夾中的所有圖片到 ImgBB
- 將圖片 URL 插入到指定的 prompt 檔案中
- 支援多種圖片格式：PNG, JPG, JPEG, GIF, WEBP

## 使用方式

### 1. 設定 API Key

複製 `scripts/imgbb_config.example.json` 為 `scripts/imgbb_config.json`，並填入您的 ImgBB API Key。

取得 API Key: https://api.imgbb.com/

### 2. 準備圖片

將要上傳的圖片放入 `Local_Media` 資料夾中。

**注意：`Local_Media` 資料夾一次僅放一種型態的圖片**

### 3. 執行腳本

```bash
python scripts/auto_upload_imgbb.py <prompt檔案名稱>
```

**參數說明：**
- `prompt檔案名稱`: prompt 檔案名稱（不含副檔名）

**範例：**
```bash
# 中文檔名
python scripts/auto_upload_imgbb.py 貪吃蛇

# 英文檔名（含空格需加引號）
python scripts/auto_upload_imgbb.py "One leaf, one world"
```

### 4. 查看結果

腳本會自動：
- 上傳所有圖片到 ImgBB
- 將圖片 URL 插入到指定的 prompt 檔案末尾
- 第一張圖片會添加 `## 範例圖片` 標題

## 目錄結構

```
AIMediaPrompt/
├── Local_Media/          # 放置要上傳的圖片
├── Prompt/Image/                # prompt 檔案存放位置
├── Prompt/Video/                # prompt 檔案存放位置
├── scripts/
│   ├── auto_upload_imgbb.py
│   ├── imgbb_config.json
│   └── imgbb_config.example.json
└── README.md
```

## 注意事項

1. 每次執行時，`Local_Media` 資料夾中應只放置一種型態的圖片
2. 如果圖片 URL 已存在於 prompt 檔案中，會自動跳過
3. 確保 prompt 檔案存在於 `Image` 資料夾中
4. 圖片會依檔名排序後依序處理

