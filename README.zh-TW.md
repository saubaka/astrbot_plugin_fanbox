<p align="center">
  <img src="https://raw.githubusercontent.com/saubaka/astrbot_plugin_fanbox/main/logo.png" width="128" height="128" alt="FANBOX 新帖推送">
</p>

<h1 align="center">FANBOX 新帖推送</h1>

<p align="center">
  <a href="https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/README.md">简体中文</a> · <b>繁體中文</b> · <a href="https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/README.ja.md">日本語</a> · <a href="https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/README.en.md">English</a>
</p>

<p align="center">訂閱 pixivFANBOX 創作者，有新貼文時推播到 QQ 群組或私聊的 AstrBot 插件</p>

<p align="center">
  <a href="https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/LICENSE"><img src="https://img.shields.io/github/license/saubaka/astrbot_plugin_fanbox?color=f0a0ba" alt="License"></a>
  <a href="https://github.com/saubaka/astrbot_plugin_fanbox/releases"><img src="https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsaubaka%2Fastrbot_plugin_fanbox%2Fmain%2Fmetadata.yaml&query=%24.version&label=version&color=8cc2ee" alt="Version"></a>
  <a href="https://github.com/AstrBotDevs/AstrBot"><img src="https://img.shields.io/badge/AstrBot-%E2%89%A5%204.26.0-8cc2ee" alt="AstrBot"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-a29ba0" alt="Python">
  <img src="https://img.shields.io/badge/platform-aiocqhttp-a29ba0" alt="Platform">
</p>

## 簡介

這是一個 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。訂閱 [pixivFANBOX](https://www.fanbox.cc) 的創作者之後，創作者發布新貼文時，插件會把訊息推播到訂閱時所在的群組或私聊。

推播有兩種樣式。文字樣式依照「推送模板」產生訊息，模板裡的內容可以用變數自由組合，也可以在任意位置插入圖片。卡片圖樣式會產生一張和 FANBOX 網頁貼文卡片相似的圖片，上面有封面、頭像、名稱、日期、方案、標題、摘要和按讚數，卡片圖上下還可以搭配文字，例如在圖片下方放貼文連結。

插件還附帶一個插件頁面，可以查看推播紀錄、管理訂閱、修改全部設定，並即時預覽推播效果。

R-18 貼文預設不發送封面，卡片圖上的封面會換成「R-18 · 封面已隱藏」，避免在 QQ 群組裡出現成人圖片。

## 安裝

在 AstrBot 管理面板中依序開啟「插件 → 安裝插件 → 從連結安裝」，填入 `https://github.com/saubaka/astrbot_plugin_fanbox` 即可。也可以手動安裝：把本儲存庫放到 AstrBot 的 `data/plugins/astrbot_plugin_fanbox` 目錄，然後重新啟動 AstrBot，或是在面板裡重新載入插件。

插件依賴 `httpx` 和 `Pillow`，AstrBot 已經內建。產生卡片圖需要中日文字型，插件預設使用系統中的 Noto Sans CJK（Debian 和 Ubuntu 的套件名稱為 `fonts-noto-cjk`），也可以在設定中指定其他字型檔。

插件需要 AstrBot v4.26.0 或更新版本，已在 aiocqhttp（OneBot v11）平台上測試過。

## 指令

| 指令 | 別名 | 作用 |
|---|---|---|
| `/fanbox关注 <創作者ID或主頁連結>` | `fanbox_follow` | 在目前的對話中訂閱這位創作者 |
| `/fanbox取关 <創作者ID>` | `fanbox_unfollow` | 取消目前對話的訂閱 |
| `/fanbox列表` | `fanbox_list` | 查看目前對話訂閱了哪些創作者，以及各自的推播起點 |
| `/fanbox最新 <創作者ID>` | `fanbox_latest` | 依照目前的推播樣式發送這位創作者的最新一篇，用來預覽樣式，不影響推播進度 |
| `/fanbox变量` | `fanbox_vars` | 列出模板中可以使用的全部變數 |
| `/fanbox检查` | `fanbox_check` | 立即檢查一次全部訂閱（僅限管理員） |

指令本身使用簡體字，輸入時請照上表的寫法，或使用英文別名。創作者 ID 就是主頁網址 `https://<ID>.fanbox.cc` 中的 `<ID>`，也可以直接貼上 `https://www.fanbox.cc/@<ID>` 這樣的連結。

## 插件頁面：FANBOX 推送面板

在 AstrBot 管理面板中開啟「插件頁面 → FANBOX 新帖推送」。頁面左上角可以切換分區，右側的「本頁章節」欄可以直接跳到目前分區的各個小節，畫面較窄時會變成頂部的一排按鈕。頁面資料每 30 秒自動更新一次。

| 分區 | 內容 |
|---|---|
| 概覽 | 近 24 小時的推播數和每小時趨勢，以及訂閱的創作者數、檢查次數、下次檢查倒數、近 7 天推播數、錯誤數和總推播數。每位創作者有一張卡片，顯示推播篇數、檢查結果、每小時的檢查情況和最新貼文，按「預覽樣式」可以直接跳到即時預覽。 |
| 推播紀錄 | 預設以 FANBOX 網頁的貼文卡片樣式顯示，封面左下角標明推播到了哪個對話、使用的樣式以及是否送達。紀錄依日期分組，也可以切換成清單。下方是最近的錯誤。 |
| 訂閱 | 可以從 QQ 群組清單中選擇群組新增訂閱，也可以填 QQ 號碼訂閱私聊。每個對話各自獨立一區，可以預覽或取消訂閱。 |
| 推播樣式 | 選好推播樣式後，下方只顯示這種樣式用得到的設定：文字模板對應推送模板，卡片圖對應卡片圖配文和卡片圖外觀，切換時會有過渡動畫。模板中的變數按一下就能插入。右側是即時預覽，畫面較窄時排在設定下方。填入貼文連結（`https://<ID>.fanbox.cc/posts/<貼文編號>`）或創作者 ID 後，修改任何一項設定都會依新樣式重新產生，尚未儲存的修改也會反映在預覽中，預覽裡的一個對話泡泡就是 QQ 中的一則訊息。預覽下方可以測試推播，把這則訊息實際發送到選定的對話或私聊，需要按兩次確認。測試推播不影響訂閱進度，不計入統計，在推播紀錄中會標示為「測試」。 |
| 設定 | 基本設定和推播起點。 |

設定儲存後立即生效，不需要重新啟動，修改輪詢間隔後會馬上依新的間隔重新計時。

預覽指定貼文時，插件會在創作者的貼文清單中往前翻頁尋找，最多翻 30 頁。貼文會快取 5 分鐘，圖片會快取 30 分鐘，所以反覆調整樣式時預覽會很快。

統計資料儲存在插件資料 `fanbox_stats_v1` 中。每小時的統計保留 90 天，推播紀錄和錯誤各保留最近 60 筆，錯誤最多保留 30 天。

AstrBot 的插件頁面執行在受限的 iframe 中，無法開啟新視窗，所以頁面上的連結都做成了「複製連結」按鈕。

## 推播起點

插件預設只推播部署之後發布的貼文，不會把以前的貼文翻出來推播。

| 起點（`start_from`） | 推播哪些貼文 |
|---|---|
| `deploy`（預設） | 插件第一次啟動之後發布的貼文。部署之後、訂閱之前發布的貼文，會在訂閱後的下一次檢查時補推，每次最多推 `max_new_posts_per_poll` 篇。 |
| `subscribe` | 每個訂閱從訂閱的那一刻開始計算，訂閱前已發布的貼文都不推播。 |
| `custom` | `start_time` 指定時間之後發布的貼文。時間寫成 `2026-11-15 08:00`，依照「時區」設定解讀，也可以寫成帶時區的 `2026-11-15T08:00:00+09:00`。格式不正確時會改用 `deploy`，並在日誌中提示。 |

插件第一次啟動的時間儲存在插件資料 `fanbox_deployed_at` 中，之後升級或重新啟動都不會改變。

`max_post_age_hours` 設為正數時，發布時間超過這個小時數的貼文不會推播。例如機器人停了很久再恢復時，不會一次補推一大堆舊貼文。預設值 0 表示不限制。

無論選擇哪種起點，同一篇貼文在同一個對話中只會推播一次。

## 設定

設定分為 5 組，可以在插件頁面或 AstrBot 內建的插件設定中修改。插件設定同樣只顯示目前推播樣式用得到的項目，但沒有訂閱管理、即時預覽和測試推播，建議使用插件頁面。

**基本設定**

| 設定項目 | 預設值 | 說明 |
|---|---|---|
| `poll_interval_minutes` | 10 | 輪詢間隔，最少 5 分鐘。每次檢查時，每位創作者只請求一次貼文清單。 |
| `max_new_posts_per_poll` | 3 | 每次檢查時，每位創作者最多推播幾篇 |
| `proxy` | 空 | 存取 FANBOX 時使用的代理伺服器 |

**推播起點**

| 設定項目 | 預設值 | 說明 |
|---|---|---|
| `start_from` | deploy | 見上一節 |
| `start_time` | 空 | 選擇 `custom` 時的起點時間 |
| `max_post_age_hours` | 0 | 不推播發布超過這個小時數的貼文，0 表示不限制 |

**推播樣式**

| 設定項目 | 預設值 | 說明 |
|---|---|---|
| `push_style` | card | `text` 依照推送模板發送；`card` 依照卡片圖配文模板發送卡片圖，卡片圖產生失敗時改為依照推送模板發送 |
| `card_text` | merge | 卡片圖的配文方式，只在 `card` 樣式下生效。`merge` 依照配文模板的順序把文字和卡片圖合成一則訊息，`separate` 以卡片圖為界把上方文字、卡片圖和下方文字分開發送，`none` 只發送卡片圖 |
| `message_template` | 見下文 | 推送模板，`text` 樣式使用，清空即恢復預設 |
| `card_template` | 見下文 | 卡片圖配文模板，`card` 樣式使用，必須保留一個 `{card_image}`，清空即恢復預設 |
| `send_cover` | 關 | 文字模板樣式下，控制模板中的 `{cover_image}` 是否發送 |
| `send_adult_cover` | 關 | R-18 貼文也發送封面，卡片圖中也顯示真實封面 |
| `creator_cover_fallback` | 開 | 貼文沒有設定封面時，改用創作者主頁的封面圖，FANBOX 分享這類貼文時也是這樣處理的。對卡片圖和 `{cover_image}` 都有效，關閉後卡片圖會顯示灰色佔位圖 |

**顯示內容**（同時作用於模板和卡片圖）

| 設定項目 | 預設值 | 說明 |
|---|---|---|
| `show_fee` | 開 | 顯示付費方案 |
| `show_timezone` | 關 | 在時間後面加上「（日本时间）」這樣的時區名稱 |
| `show_tags` | 開 | 顯示標籤 |
| `show_adult_mark` | 開 | 顯示 R-18 標記 |
| `excerpt_max_chars` | 120 | `{excerpt}` 的最大長度，設為 0 則不顯示 |
| `max_tags` | 6 | 最多顯示幾個標籤 |
| `time_format` | `%Y-%m-%d %H:%M` | `{published}` 和 `{updated}` 的時間格式（strftime 寫法） |
| `timezone_offset_hours` | 9 | 時區，9 表示日本時間（與 FANBOX 網頁一致），8 表示北京時間（UTC+8，與台灣相同） |

**卡片圖**

| 設定項目 | 預設值 | 說明 |
|---|---|---|
| `card_show_likes` | 開 | 在右下角顯示按讚數 |
| `card_excerpt_lines` | 2 | 摘要最多顯示幾行，設為 0 則不顯示 |
| `card_title_lines` | 2 | 標題最多顯示幾行 |
| `card_font_path` / `card_bold_font_path` | 空 | 自訂字型檔，留空時使用 Noto Sans CJK |

卡片圖寬 1430 像素，相當於網頁在 2 倍螢幕上的尺寸，格式為 JPEG，大小約 150 到 400 KB。彩色 emoji 沒有對應的字型，在卡片圖中會被省略，文字訊息中的 emoji 不受影響。

## 推送模板

插件輸出的文字是簡體中文，下面的模板和範例值也保留原樣。預設模板如下：

```
【FANBOX】{creator_name} {headline}
《{title}》
{labels}
{excerpt}
{tags}
?发布时间：{published}
{post_url}
{cover_image}
```

### 卡片圖配文模板

推播樣式為 `card` 時使用這個模板。模板中的 `{card_image}` 就是卡片圖本身，必須保留，而且只能有一個。插件頁面的編輯器中刪不掉它；如果模板中沒有，插件會自動把它補在末尾。寫在 `{card_image}` 上面的文字顯示在卡片圖上方，寫在下面的文字顯示在卡片圖下方。其他變數和寫法規則與推送模板相同，但其他圖片變數在這裡會被忽略，因為卡片圖中已經有封面和頭像。預設模板在卡片圖上方放作者名稱和一句提示：

```
{creator_name}
发布了新的FANBOX文章：
{card_image}
```

`card_text` 選擇 `merge` 時，上面這些內容在 QQ 中是一則訊息，文字在上，卡片圖在下。想在卡片圖下方放貼文連結，在 `{card_image}` 下面加一行 `{post_url}` 即可。選擇 `separate`（插件頁面中叫「分开发」）時，會以卡片圖為界分開，上方文字、卡片圖和下方文字各發一則。選擇 `none` 時只發送卡片圖，不使用模板。

在插件頁面中，可以用「把卡片图移到光标处」按鈕調整卡片圖在模板中的位置。

### 寫法規則

1. `{變數}` 會替換成對應的值，變數名稱區分大小寫。
2. `{{` 和 `}}` 表示大括號本身。
3. 無法識別的 `{xxx}` 會原樣顯示，插件載入時會在日誌中提示。
4. 如果一行中的變數都是空的，而且這一行沒有其他文字，這一行會被自動刪除。
5. 以 `?` 開頭的行是條件行，只要行中有一個變數是空的，整行就會被刪除，`?` 本身不會顯示，例如 `?发布时间：{published}`。
6. 圖片變數寫在哪裡，圖片就出現在訊息的哪個位置。
7. 模板為空時使用預設模板。

### 文字變數（30 個）

範例值來自一篇 500 日圓方案的付費貼文，所有設定都是預設值。

| 變數 | 意義 | 範例值 |
|---|---|---|
| `{headline}` | 推播時是「发布了新帖」，使用 /fanbox最新 時是「的最新帖子」 | `发布了新帖` |
| `{creator_name}` | 創作者暱稱 | `pixivFANBOX公式` |
| `{creator_id}` | 創作者 ID，也就是主頁 https://<ID>.fanbox.cc 中的 <ID> | `official` |
| `{creator_url}` | 創作者主頁連結 | `https://official.fanbox.cc` |
| `{creator_icon_url}` | 創作者頭像的圖片連結 | `https://pixiv.pximg.net/c/160x160_90_a2_g5/fanbox/public/…` |
| `{title}` | 貼文標題，沒有標題時是「（无标题）」 | `新作イラストのお知らせ` |
| `{post_id}` | 貼文 ID | `1234567` |
| `{post_url}` | 貼文連結 | `https://official.fanbox.cc/posts/1234567` |
| `{excerpt}` | 摘要，依照「摘要最多顯示多少字」截斷，付費貼文通常沒有摘要 | `いつも応援ありがとうございます。今月の新作です。` |
| `{excerpt_full}` | 完整摘要，只整理空行，不截斷 | `いつも応援ありがとうございます。今月の新作です。` |
| `{fee}` | 方案金額，免費貼文為 0，不受「顯示付費方案」影響 | `500` |
| `{fee_text}` | 「付费 · 500 日元及以上档位」或「免费公开」，關閉「顯示付費方案」時為空 | `付费 · 500 日元及以上档位` |
| `{fee_badge}` | 「500日元」或「免费」，關閉「顯示付費方案」時為空 | `500日元` |
| `{paid}` | 「付费」或「免费」，不受「顯示付費方案」影響 | `付费` |
| `{adult}` | R-18 貼文為「R-18」，其他貼文為空，關閉「顯示 R-18 標記」時也為空 | （空） |
| `{labels}` | 用「 · 」連接的方案和 R-18 標記，例如「付费 · 500 日元及以上档位 · R-18」 | `付费 · 500 日元及以上档位` |
| `{restricted}` | 需要贊助才能查看內文時為「需赞助」，否則為空 | `需赞助` |
| `{tags}` | 標籤，寫成「#標籤1 #標籤2」，關閉「顯示標籤」時為空 | `#イラスト #メイキング` |
| `{tags_plain}` | 標籤，用頓號連接成「標籤1、標籤2」，關閉「顯示標籤」時為空 | `イラスト、メイキング` |
| `{tag_count}` | 標籤數量 | `2` |
| `{published}` | 發布時間，依照「時間格式」和時區顯示，開啟「顯示時區」時後面帶「（北京时间）」 | `2026-11-13 21:12` |
| `{published_date}` | 發布日期，例如 2026-11-13 | `2026-11-13` |
| `{published_time}` | 發布時刻，例如 20:12 | `21:12` |
| `{published_iso}` | FANBOX 原始的發布時間，日本時間的 ISO 格式 | `2026-11-13T21:12:54+09:00` |
| `{updated}` | 最後更新時間，格式和 published 相同 | `2026-11-14 09:30` |
| `{timezone}` | 時區名稱，例如「北京时间」，不受「顯示時區」影響 | `日本时间` |
| `{like_count}` | 按讚數 | `12` |
| `{comment_count}` | 留言數 | `3` |
| `{cover_url}` | 封面圖連結。貼文沒有設定封面時，依照設定改用創作者主頁封面；R-18 貼文在不允許發送封面時為空 | `https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public…` |
| `{pinned}` | 置頂貼文為「置顶」，否則為空 | （空） |

### 圖片變數（3 個）

| 變數 | 意義 |
|---|---|
| `{cover_image}` | 封面圖。貼文沒有設定封面時，依照設定改用創作者主頁封面；關閉「附帶封面圖」，或 R-18 貼文不允許發送封面時不發送 |
| `{card_image}` | 仿照 FANBOX 網頁樣式的卡片圖 |
| `{avatar_image}` | 創作者頭像 |

### 模板範例

只發送卡片圖，並在下面加一行連結：

```
{card_image}
{post_url}
```

簡短的一行：

```
{creator_name} 更新了《{title}》 {fee_badge} {post_url}
```

頭像加上詳細資訊：

```
{avatar_image}
{creator_name}（{creator_id}）{headline}
《{title}》 {labels}
?标签：{tags_plain}
?{published_date} {published_time} {timezone}
♥ {like_count}  评论 {comment_count}
{post_url}
{cover_image}
```

## 已知限制

有些貼文作者沒有設定封面，FANBOX 網頁上只會顯示灰色的佔位圖。遇到這種情況，插件預設改用創作者主頁的封面，也可以在設定中關閉。

每次檢查只看每位創作者最新的 10 篇貼文。如果兩次檢查之間某位創作者發了超過 10 篇，較早的幾篇不會被推播。

訂閱紀錄儲存在 AstrBot 的插件資料中，鍵名是 `fanbox_subscriptions_v1`。

## 開發

```bash
python -m pytest -q tests
python -m ruff check .
python -m ruff format --check .
python -m compileall -q .
python -m json.tool _conf_schema.json
```

`fanbox_core.py`、`fanbox_api.py`、`fanbox_card.py`、`fanbox_stats.py` 和 `fanbox_settings.py` 不依賴 AstrBot。`fanbox_webui.py` 是插件頁面的後端介面，`pages/dashboard/` 是前端頁面。執行測試需要 `httpx`、`pytest` 和 `Pillow`，沒有 Noto Sans CJK 字型時會跳過卡片圖相關的測試。

## 授權

本插件採用 MIT 授權，詳見 [LICENSE](https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/LICENSE)。
