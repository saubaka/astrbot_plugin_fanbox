<p align="center">
  <img src="https://raw.githubusercontent.com/saubaka/astrbot_plugin_fanbox/main/logo.png" width="128" height="128" alt="FANBOX 新帖推送">
</p>

<h1 align="center">FANBOX 新帖推送</h1>

<p align="center">订阅 pixivFANBOX 创作者，有新帖时推送到 QQ 群聊或私聊的 AstrBot 插件</p>

<p align="center">
  <a href="https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/LICENSE"><img src="https://img.shields.io/github/license/saubaka/astrbot_plugin_fanbox?color=f0a0ba" alt="License"></a>
  <a href="https://github.com/saubaka/astrbot_plugin_fanbox/releases"><img src="https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsaubaka%2Fastrbot_plugin_fanbox%2Fmain%2Fmetadata.yaml&query=%24.version&label=version&color=8cc2ee" alt="Version"></a>
  <a href="https://github.com/AstrBotDevs/AstrBot"><img src="https://img.shields.io/badge/AstrBot-%E2%89%A5%204.26.0-8cc2ee" alt="AstrBot"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-a29ba0" alt="Python">
  <img src="https://img.shields.io/badge/platform-aiocqhttp-a29ba0" alt="Platform">
</p>

<p align="center">点击语言名称展开或收起 · 點擊語言名稱展開或收合 · 言語名をクリックして開閉 · Click a language to expand or collapse</p>

<details open>
<summary><b>简体中文</b></summary>

## 简介

这是一个 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。订阅 [pixivFANBOX](https://www.fanbox.cc) 的创作者之后，创作者发布新帖时，插件会把消息推送到订阅时所在的群聊或私聊。

推送有两种样式。文字样式按“推送模板”生成消息，模板里的内容可以用变量自由组合，也可以在任意位置插入图片。卡片图样式会生成一张和 FANBOX 网页帖子卡片相似的图片，上面有封面、头像、名字、日期、档位、标题、摘要和点赞数，卡片图上下还可以配文字，比如在图片下方放帖子链接。

插件还带有一个插件页，可以查看推送记录、管理订阅、修改全部设置，并实时预览推送效果。

R-18 帖子默认不发封面，卡片图上的封面会换成“R-18 · 封面已隐藏”，避免在 QQ 群里出现成人图片。

## 安装

在 AstrBot 管理面板中依次打开“插件 → 安装插件 → 从链接安装”，填入 `https://github.com/saubaka/astrbot_plugin_fanbox` 即可。也可以手动安装：把本仓库放到 AstrBot 的 `data/plugins/astrbot_plugin_fanbox` 目录，然后重启 AstrBot，或者在面板里重载插件。

插件依赖 `httpx` 和 `Pillow`，AstrBot 已经自带。生成卡片图需要中日文字体，插件默认使用系统里的 Noto Sans CJK（Debian 和 Ubuntu 的软件包名为 `fonts-noto-cjk`），也可以在配置里指定其他字体文件。

插件需要 AstrBot v4.26.0 或更高版本，在 aiocqhttp（OneBot v11）平台上测试过。

## 指令

| 指令 | 别名 | 作用 |
|---|---|---|
| `/fanbox关注 <创作者ID或主页链接>` | `fanbox_follow` | 在当前会话订阅这位创作者 |
| `/fanbox取关 <创作者ID>` | `fanbox_unfollow` | 取消当前会话的订阅 |
| `/fanbox列表` | `fanbox_list` | 查看当前会话订阅了哪些创作者，以及各自的推送起点 |
| `/fanbox最新 <创作者ID>` | `fanbox_latest` | 按当前推送样式发送这位创作者的最新一篇，用来预览样式，不影响推送进度 |
| `/fanbox变量` | `fanbox_vars` | 列出模板里可以使用的全部变量 |
| `/fanbox检查` | `fanbox_check` | 立即检查一次全部订阅（仅管理员可用） |

创作者 ID 就是主页地址 `https://<ID>.fanbox.cc` 中的 `<ID>`。也可以直接粘贴 `https://www.fanbox.cc/@<ID>` 这样的链接。

## 插件页：FANBOX 推送面板

在 AstrBot 管理面板中打开“插件页面 → FANBOX 新帖推送”。页面左上角可以切换分区，右侧的“本页章节”栏可以直接跳到当前分区的各个小节，窄屏时会变成顶部的一排按钮。页面数据每 30 秒自动刷新一次。

| 分区 | 内容 |
|---|---|
| 概览 | 近 24 小时的推送数和每小时趋势，以及订阅的创作者数、检查次数、下次检查倒计时、近 7 天推送数、报错数和总推送数。每位创作者有一张卡片，显示推送篇数、检查结果、每小时的检查情况和最新帖子，点“预览样式”可以直接跳到实时预览。 |
| 推送记录 | 默认用 FANBOX 网页的帖子卡片样式展示，封面左下角标明推送到了哪个会话、使用的样式以及是否送达。记录按天分组，也可以切换成列表。下方是最近的报错。 |
| 订阅 | 可以从 QQ 群列表里选群添加订阅，也可以填 QQ 号订阅私聊。每个会话单独一块，可以预览或取消订阅。 |
| 推送样式 | 包括推送样式、推送模板、卡片图配文、显示内容和卡片图五组设置，模板里的变量点一下就能插入。右侧是实时预览，窄屏时排在设置下方。填入帖子链接（`https://<ID>.fanbox.cc/posts/<帖子号>`）或创作者 ID 后，修改任何一项设置都会按新样式重新生成，未保存的修改也会体现在预览里，预览中的一个气泡就是 QQ 里的一条消息。预览下方可以测试推送，把这条消息实际发到选定的会话或私聊，需要点两次确认。测试推送不影响订阅进度，不计入统计，在推送记录里会标为“测试”。 |
| 设置 | 基础设置和推送起点。 |

设置保存后立即生效，不需要重启，修改轮询间隔后会马上按新的间隔重新计时。

预览指定帖子时，插件会在创作者的帖子列表里往前翻页查找，最多翻 30 页。帖子会缓存 5 分钟，图片会缓存 30 分钟，所以反复调整样式时预览会很快。

统计数据保存在插件数据 `fanbox_stats_v1` 中。按小时的统计保留 90 天，推送记录和报错各保留最近 60 条，报错最多保留 30 天。

AstrBot 的插件页运行在受限的 iframe 里，不能打开新窗口，所以页面上的链接都做成了“复制链接”按钮。

## 推送起点

插件默认只推送部署之后发布的帖子，不会把以前的帖子翻出来推送。

| 起点（`start_from`） | 推送哪些帖子 |
|---|---|
| `deploy`（默认） | 插件第一次启动之后发布的帖子。部署之后、订阅之前发布的帖子，会在订阅后的下一次检查时补推，每次最多推 `max_new_posts_per_poll` 篇。 |
| `subscribe` | 每个订阅从订阅的那一刻开始计算，订阅前已经发布的帖子都不推送。 |
| `custom` | `start_time` 指定时间之后发布的帖子。时间写成 `2026-11-15 08:00`，按“时区”设置来理解，也可以写带时区的 `2026-11-15T08:00:00+09:00`。格式不正确时会改用 `deploy`，并在日志里提示。 |

插件第一次启动的时间保存在插件数据 `fanbox_deployed_at` 中，之后升级或重启都不会改变。

`max_post_age_hours` 设为正数时，发布时间超过这个小时数的帖子不会推送。比如机器人停了很久再恢复，不会一次补推一大堆旧帖。默认值 0 表示不限制。

无论选择哪种起点，同一篇帖子在同一个会话里只会推送一次。

## 配置

配置分为 5 组，可以在 AstrBot 面板或插件页里修改。

**基础设置**

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `poll_interval_minutes` | 10 | 轮询间隔，最少 5 分钟。每次检查时，每位创作者只请求一次帖子列表。 |
| `max_new_posts_per_poll` | 3 | 每次检查时，每位创作者最多推送几篇 |
| `proxy` | 空 | 访问 FANBOX 时使用的代理 |

**推送起点**

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `start_from` | deploy | 见上一节 |
| `start_time` | 空 | 选择 `custom` 时的起点时间 |
| `max_post_age_hours` | 0 | 不推送发布超过这个小时数的帖子，0 表示不限制 |

**推送样式**

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `push_style` | text | `text` 按推送模板发送；`card` 按卡片图配文模板发送卡片图，卡片图生成失败时改为按推送模板发送 |
| `card_text` | merge | 卡片图的配文方式，只在 `card` 样式下生效。`merge` 按配文模板的顺序把文字和卡片图合成一条消息，`separate` 以卡片图为界把上方文字、卡片图和下方文字分开发送，`none` 只发卡片图 |
| `message_template` | 见下文 | 推送模板，`text` 样式使用，清空即恢复默认 |
| `card_template` | 见下文 | 卡片图配文模板，`card` 样式使用，必须保留一个 `{card_image}`，清空即恢复默认 |
| `send_cover` | 开 | 控制模板里的 `{cover_image}` 是否发送 |
| `send_adult_cover` | 关 | R-18 帖子也发送封面，卡片图里也显示真实封面 |
| `creator_cover_fallback` | 开 | 帖子没有设置封面时，改用创作者主页的封面图，FANBOX 分享这类帖子时也是这样做的。对卡片图和 `{cover_image}` 都生效，关闭后卡片图会显示灰色占位图 |

**显示内容**（同时作用于模板和卡片图）

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `show_fee` | 开 | 显示付费档位 |
| `show_timezone` | 开 | 在时间后面加上“（北京时间）”这样的时区名称 |
| `show_tags` | 开 | 显示标签 |
| `show_adult_mark` | 开 | 显示 R-18 标记 |
| `excerpt_max_chars` | 120 | `{excerpt}` 的最大长度，设为 0 则不显示 |
| `max_tags` | 6 | 最多显示几个标签 |
| `time_format` | `%Y-%m-%d %H:%M` | `{published}` 和 `{updated}` 的时间格式（strftime 写法） |
| `timezone_offset_hours` | 8 | 时区，8 表示北京时间，9 表示日本时间 |

**卡片图**

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `card_show_likes` | 开 | 在右下角显示点赞数 |
| `card_excerpt_lines` | 2 | 摘要最多显示几行，设为 0 则不显示 |
| `card_title_lines` | 2 | 标题最多显示几行 |
| `card_font_path` / `card_bold_font_path` | 空 | 自定义字体文件，留空时使用 Noto Sans CJK |

卡片图宽 1430 像素，相当于网页在 2 倍屏上的尺寸，格式为 JPEG，大小约 150 到 400 KB。彩色 emoji 没有对应的字体，在卡片图里会被省略，文字消息里的 emoji 不受影响。

## 推送模板

默认模板如下：

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

### 卡片图配文模板

推送样式为 `card` 时使用这个模板。模板里的 `{card_image}` 就是卡片图本身，必须保留，而且只能有一个。插件页的编辑器里删不掉它；如果模板里没有，插件会自动把它补在末尾。写在 `{card_image}` 上面的文字显示在卡片图上方，写在下面的文字显示在卡片图下方。其他变量和写法规则与推送模板相同，但其他图片变量在这里会被忽略，因为卡片图里已经有封面和头像。默认模板在卡片图上方放标题，下方放链接：

```
【FANBOX】{creator_name} {headline}
《{title}》
{card_image}
{post_url}
```

`card_text` 选择 `merge` 时，上面这些内容在 QQ 里是一条消息，标题在上，卡片图在中间，链接在卡片图下方。选择 `separate`（插件页里叫“分开发”）时，会以卡片图为界分开，上方文字、卡片图和下方文字各发一条。选择 `none` 时只发卡片图，不使用模板。

在插件页里，可以用“把卡片图移到光标处”按钮调整卡片图在模板里的位置。

### 写法规则

1. `{变量}` 会替换成对应的值，变量名区分大小写。
2. `{{` 和 `}}` 表示花括号本身。
3. 无法识别的 `{xxx}` 会原样显示，插件加载时会在日志里提示。
4. 如果一行里的变量都为空，而且这一行没有其他文字，这一行会被自动删掉。
5. 以 `?` 开头的行是条件行，只要行里有一个变量为空，整行就会被删掉，`?` 本身不会显示，例如 `?发布时间：{published}`。
6. 图片变量写在哪里，图片就出现在消息的哪个位置。
7. 模板为空时使用默认模板。

### 文字变量（30 个）

示例值来自一篇 500 日元档的付费帖，所有配置都是默认值。

| 变量 | 含义 | 示例值 |
|---|---|---|
| `{headline}` | 推送时是“发布了新帖”，使用 /fanbox最新 时是“的最新帖子” | `发布了新帖` |
| `{creator_name}` | 创作者昵称 | `pixivFANBOX公式` |
| `{creator_id}` | 创作者 ID，也就是主页 https://<ID>.fanbox.cc 中的 <ID> | `official` |
| `{creator_url}` | 创作者主页链接 | `https://official.fanbox.cc` |
| `{creator_icon_url}` | 创作者头像的图片链接 | `https://pixiv.pximg.net/c/160x160_90_a2_g5/fanbox/public/…` |
| `{title}` | 帖子标题，没有标题时是“（无标题）” | `新作イラストのお知らせ` |
| `{post_id}` | 帖子 ID | `1234567` |
| `{post_url}` | 帖子链接 | `https://official.fanbox.cc/posts/1234567` |
| `{excerpt}` | 摘要，按“摘要最多显示多少字”截断，付费帖通常没有摘要 | `いつも応援ありがとうございます。今月の新作です。` |
| `{excerpt_full}` | 完整摘要，只整理空行，不截断 | `いつも応援ありがとうございます。今月の新作です。` |
| `{fee}` | 档位金额，免费帖为 0，不受“显示付费档位”影响 | `500` |
| `{fee_text}` | “付费 · 500 日元及以上档位”或“免费公开”，关闭“显示付费档位”时为空 | `付费 · 500 日元及以上档位` |
| `{fee_badge}` | “500日元”或“免费”，关闭“显示付费档位”时为空 | `500日元` |
| `{paid}` | “付费”或“免费”，不受“显示付费档位”影响 | `付费` |
| `{adult}` | R-18 帖子为“R-18”，其他帖子为空，关闭“显示 R-18 标记”时也为空 | （空） |
| `{labels}` | 用“ · ”连接的档位和 R-18 标记，例如“付费 · 500 日元及以上档位 · R-18” | `付费 · 500 日元及以上档位` |
| `{restricted}` | 需要赞助才能查看正文时为“需赞助”，否则为空 | `需赞助` |
| `{tags}` | 标签，写成“#标签1 #标签2”，关闭“显示标签”时为空 | `#イラスト #メイキング` |
| `{tags_plain}` | 标签，用顿号连接成“标签1、标签2”，关闭“显示标签”时为空 | `イラスト、メイキング` |
| `{tag_count}` | 标签个数 | `2` |
| `{published}` | 发布时间，按“时间格式”和时区显示，开启“显示时区”时后面带“（北京时间）” | `2026-11-13 20:12（北京时间）` |
| `{published_date}` | 发布日期，例如 2026-11-13 | `2026-11-13` |
| `{published_time}` | 发布时刻，例如 20:12 | `20:12` |
| `{published_iso}` | FANBOX 原始的发布时间，日本时间的 ISO 格式 | `2026-11-13T21:12:54+09:00` |
| `{updated}` | 最后更新时间，格式和 published 相同 | `2026-11-14 08:30（北京时间）` |
| `{timezone}` | 时区名称，例如“北京时间”，不受“显示时区”影响 | `北京时间` |
| `{like_count}` | 点赞数 | `12` |
| `{comment_count}` | 评论数 | `3` |
| `{cover_url}` | 封面图链接。帖子没有设置封面时，按设置改用创作者主页封面；R-18 帖子在不允许发封面时为空 | `https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public…` |
| `{pinned}` | 置顶帖为“置顶”，否则为空 | （空） |

### 图片变量（3 个）

| 变量 | 含义 |
|---|---|
| `{cover_image}` | 封面图。帖子没有设置封面时，按设置改用创作者主页封面；关闭“附带封面图”，或 R-18 帖子不允许发封面时不发送 |
| `{card_image}` | 仿照 FANBOX 网页样式的卡片图 |
| `{avatar_image}` | 创作者头像 |

### 模板示例

只发卡片图，并在下面加一行链接：

```
{card_image}
{post_url}
```

简短的一行：

```
{creator_name} 更新了《{title}》 {fee_badge} {post_url}
```

头像加上详细信息：

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

有些帖子作者没有设置封面，FANBOX 网页上只会显示灰色的占位图。遇到这种情况，插件默认改用创作者主页的封面，也可以在设置里关闭。

每次检查只看每位创作者最新的 10 篇帖子。如果两次检查之间某位创作者发了超过 10 篇，较早的几篇不会被推送。

订阅记录保存在 AstrBot 的插件数据里，键名是 `fanbox_subscriptions_v1`。

## 开发

```bash
python -m pytest -q tests
python -m ruff check .
python -m ruff format --check .
python -m compileall -q .
python -m json.tool _conf_schema.json
```

`fanbox_core.py`、`fanbox_api.py`、`fanbox_card.py`、`fanbox_stats.py` 和 `fanbox_settings.py` 不依赖 AstrBot。`fanbox_webui.py` 是插件页的后端接口，`pages/dashboard/` 是前端页面。运行测试需要 `httpx`、`pytest` 和 `Pillow`，没有 Noto Sans CJK 字体时会跳过卡片图相关的测试。

## 许可证

本插件使用 MIT 许可证，详见 [LICENSE](https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/LICENSE)。

</details>

<details>
<summary><b>繁體中文</b></summary>

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
| 推播樣式 | 包含推播樣式、推送模板、卡片圖配文、顯示內容和卡片圖五組設定，模板中的變數按一下就能插入。右側是即時預覽，畫面較窄時排在設定下方。填入貼文連結（`https://<ID>.fanbox.cc/posts/<貼文編號>`）或創作者 ID 後，修改任何一項設定都會依新樣式重新產生，尚未儲存的修改也會反映在預覽中，預覽裡的一個對話泡泡就是 QQ 中的一則訊息。預覽下方可以測試推播，把這則訊息實際發送到選定的對話或私聊，需要按兩次確認。測試推播不影響訂閱進度，不計入統計，在推播紀錄中會標示為「測試」。 |
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

設定分為 5 組，可以在 AstrBot 面板或插件頁面中修改。

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
| `push_style` | text | `text` 依照推送模板發送；`card` 依照卡片圖配文模板發送卡片圖，卡片圖產生失敗時改為依照推送模板發送 |
| `card_text` | merge | 卡片圖的配文方式，只在 `card` 樣式下生效。`merge` 依照配文模板的順序把文字和卡片圖合成一則訊息，`separate` 以卡片圖為界把上方文字、卡片圖和下方文字分開發送，`none` 只發送卡片圖 |
| `message_template` | 見下文 | 推送模板，`text` 樣式使用，清空即恢復預設 |
| `card_template` | 見下文 | 卡片圖配文模板，`card` 樣式使用，必須保留一個 `{card_image}`，清空即恢復預設 |
| `send_cover` | 開 | 控制模板中的 `{cover_image}` 是否發送 |
| `send_adult_cover` | 關 | R-18 貼文也發送封面，卡片圖中也顯示真實封面 |
| `creator_cover_fallback` | 開 | 貼文沒有設定封面時，改用創作者主頁的封面圖，FANBOX 分享這類貼文時也是這樣處理的。對卡片圖和 `{cover_image}` 都有效，關閉後卡片圖會顯示灰色佔位圖 |

**顯示內容**（同時作用於模板和卡片圖）

| 設定項目 | 預設值 | 說明 |
|---|---|---|
| `show_fee` | 開 | 顯示付費方案 |
| `show_timezone` | 開 | 在時間後面加上「（北京时间）」這樣的時區名稱 |
| `show_tags` | 開 | 顯示標籤 |
| `show_adult_mark` | 開 | 顯示 R-18 標記 |
| `excerpt_max_chars` | 120 | `{excerpt}` 的最大長度，設為 0 則不顯示 |
| `max_tags` | 6 | 最多顯示幾個標籤 |
| `time_format` | `%Y-%m-%d %H:%M` | `{published}` 和 `{updated}` 的時間格式（strftime 寫法） |
| `timezone_offset_hours` | 8 | 時區，8 表示北京時間（UTC+8，與台灣相同），9 表示日本時間 |

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

推播樣式為 `card` 時使用這個模板。模板中的 `{card_image}` 就是卡片圖本身，必須保留，而且只能有一個。插件頁面的編輯器中刪不掉它；如果模板中沒有，插件會自動把它補在末尾。寫在 `{card_image}` 上面的文字顯示在卡片圖上方，寫在下面的文字顯示在卡片圖下方。其他變數和寫法規則與推送模板相同，但其他圖片變數在這裡會被忽略，因為卡片圖中已經有封面和頭像。預設模板在卡片圖上方放標題，下方放連結：

```
【FANBOX】{creator_name} {headline}
《{title}》
{card_image}
{post_url}
```

`card_text` 選擇 `merge` 時，上面這些內容在 QQ 中是一則訊息，標題在上，卡片圖在中間，連結在卡片圖下方。選擇 `separate`（插件頁面中叫「分开发」）時，會以卡片圖為界分開，上方文字、卡片圖和下方文字各發一則。選擇 `none` 時只發送卡片圖，不使用模板。

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
| `{published}` | 發布時間，依照「時間格式」和時區顯示，開啟「顯示時區」時後面帶「（北京时间）」 | `2026-11-13 20:12（北京时间）` |
| `{published_date}` | 發布日期，例如 2026-11-13 | `2026-11-13` |
| `{published_time}` | 發布時刻，例如 20:12 | `20:12` |
| `{published_iso}` | FANBOX 原始的發布時間，日本時間的 ISO 格式 | `2026-11-13T21:12:54+09:00` |
| `{updated}` | 最後更新時間，格式和 published 相同 | `2026-11-14 08:30（北京时间）` |
| `{timezone}` | 時區名稱，例如「北京时间」，不受「顯示時區」影響 | `北京时间` |
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

</details>

<details>
<summary><b>日本語</b></summary>

## 概要

[AstrBot](https://github.com/AstrBotDevs/AstrBot) 用のプラグインです。[pixivFANBOX](https://www.fanbox.cc) のクリエイターを購読しておくと、新しい投稿があったときに、購読したグループチャットや個人チャットへ通知します。

通知のスタイルは 2 種類あります。テキストスタイルは「通知テンプレート」に沿ってメッセージを作ります。テンプレートでは変数を自由に組み合わせられ、好きな位置に画像を入れることもできます。カードスタイルは FANBOX の投稿カードに似た画像を生成します。カバー画像、アイコン、名前、日付、プラン、タイトル、抜粋、いいね数が入り、カード画像の上下には文章を添えられます。たとえば画像の下に投稿へのリンクを置くこともできます。

プラグインページも付いており、通知履歴の確認、購読の管理、すべての設定の変更、通知内容のリアルタイムプレビューができます。

R-18 の投稿は、初期設定ではカバー画像を送りません。カード画像のカバー部分は「R-18 · 封面已隐藏」に置き換わり、QQ のグループに成人向け画像が流れないようにしています。

## インストール

AstrBot の管理パネルで「プラグイン → プラグインをインストール → リンクからインストール」を開き、`https://github.com/saubaka/astrbot_plugin_fanbox` を入力します。手動でインストールする場合は、このリポジトリを AstrBot の `data/plugins/astrbot_plugin_fanbox` に置き、AstrBot を再起動するか、管理パネルでプラグインを再読み込みしてください。

依存ライブラリは `httpx` と `Pillow` で、どちらも AstrBot に含まれています。カード画像の生成には日中のフォントが必要です。初期設定ではシステムの Noto Sans CJK（Debian と Ubuntu のパッケージ名は `fonts-noto-cjk`）を使い、設定でほかのフォントファイルを指定することもできます。

AstrBot v4.26.0 以降が必要です。aiocqhttp（OneBot v11）で動作を確認しています。

## コマンド

| コマンド | 別名 | 内容 |
|---|---|---|
| `/fanbox关注 <クリエイターIDまたはページのURL>` | `fanbox_follow` | 現在の会話でこのクリエイターを購読する |
| `/fanbox取关 <クリエイターID>` | `fanbox_unfollow` | 現在の会話での購読を解除する |
| `/fanbox列表` | `fanbox_list` | 現在の会話で購読しているクリエイターと、それぞれの通知開始時点を表示する |
| `/fanbox最新 <クリエイターID>` | `fanbox_latest` | 現在の通知スタイルで最新の投稿を 1 件送る。スタイルの確認用で、通知の進み具合には影響しない |
| `/fanbox变量` | `fanbox_vars` | テンプレートで使える変数をすべて表示する |
| `/fanbox检查` | `fanbox_check` | すべての購読をすぐにチェックする（管理者のみ） |

コマンド名は中国語（簡体字）なので、上の表のとおりに入力するか、英語の別名を使ってください。クリエイター ID はページの URL `https://<ID>.fanbox.cc` の `<ID>` の部分です。`https://www.fanbox.cc/@<ID>` のようなリンクをそのまま貼り付けることもできます。

## プラグインページ：FANBOX 推送面板

AstrBot の管理パネルで「プラグインページ → FANBOX 新帖推送」を開きます。ページの左上でタブを切り替えられ、右側の「本页章节」欄から、表示中のタブの各セクションへ直接移動できます。画面が狭いときは上部のボタン列になります。データは 30 秒ごとに自動で更新されます。

| タブ | 内容 |
|---|---|
| 概览（概要） | 直近 24 時間の通知数と時間ごとの推移、購読中のクリエイター数、チェック回数、次のチェックまでの残り時間、直近 7 日の通知数、エラー数、通知の総数。クリエイターごとのカードには、通知した件数、チェック結果、時間ごとのチェック状況、最新の投稿が表示され、「预览样式」からリアルタイムプレビューへ移動できます。 |
| 推送记录（通知履歴） | 初期表示は FANBOX の投稿カード風です。カバー画像の左下に、通知先の会話、使ったスタイル、届いたかどうかが表示されます。履歴は日ごとにまとめられ、リスト表示にも切り替えられます。下には最近のエラーが表示されます。 |
| 订阅（購読） | QQ のグループ一覧からグループを選んで購読を追加できます。QQ 番号を入力すれば個人チャットでも購読できます。会話ごとに区切って表示され、プレビューや購読解除ができます。 |
| 推送样式（通知スタイル） | 通知スタイル、通知テンプレート、カードの添え文、表示内容、カード画像の 5 つの設定グループがあり、テンプレートの変数はクリックするだけで挿入できます。右側はリアルタイムプレビューで、画面が狭いときは設定の下に並びます。投稿のリンク（`https://<ID>.fanbox.cc/posts/<投稿番号>`）かクリエイター ID を入れると、設定を変えるたびに新しいスタイルで作り直され、保存前の変更もプレビューに反映されます。プレビューの吹き出し 1 つが QQ のメッセージ 1 件にあたります。プレビューの下からはテスト送信ができ、このメッセージを選んだ会話や個人チャットへ実際に送ります。送信には 2 回のクリックが必要です。テスト送信は購読の進み具合や統計には含まれず、通知履歴では「测试」と表示されます。 |
| 设置（設定） | 基本設定と通知開始時点。 |

設定は保存するとすぐに反映され、再起動は不要です。チェック間隔を変えると、新しい間隔ですぐに計測し直します。

特定の投稿をプレビューするときは、クリエイターの投稿一覧をさかのぼって探します（最大 30 ページ）。投稿は 5 分、画像は 30 分キャッシュされるので、スタイルを何度調整してもプレビューはすぐに表示されます。

統計データはプラグインデータ `fanbox_stats_v1` に保存されます。時間ごとの統計は 90 日、通知履歴とエラーはそれぞれ直近 60 件を保存し、エラーは最長 30 日で消えます。

AstrBot のプラグインページは制限付きの iframe で動いていて新しいウィンドウを開けないため、ページ内のリンクはすべて「リンクをコピー」ボタンになっています。

## 通知開始時点

初期設定では、プラグインをデプロイした後に公開された投稿だけを通知し、それ以前の投稿をさかのぼって通知することはありません。

| 開始時点（`start_from`） | 通知する投稿 |
|---|---|
| `deploy`（初期設定） | プラグインが初めて起動した後に公開された投稿。デプロイ後から購読前までに公開された投稿は、購読後の次のチェックでまとめて通知します（1 回につき最大 `max_new_posts_per_poll` 件）。 |
| `subscribe` | 購読した時点から数えます。購読前に公開された投稿は通知しません。 |
| `custom` | `start_time` で指定した時刻より後に公開された投稿。`2026-11-15 08:00` のように書くと「タイムゾーン」設定に沿って解釈され、`2026-11-15T08:00:00+09:00` のようにタイムゾーン付きでも書けます。形式が正しくない場合は `deploy` を使い、ログでお知らせします。 |

プラグインが初めて起動した時刻はプラグインデータ `fanbox_deployed_at` に保存され、アップデートや再起動では変わりません。

`max_post_age_hours` を正の数にすると、公開からその時間数を過ぎた投稿は通知しません。たとえばボットを長く止めていた後に再開しても、古い投稿がまとめて通知されることはありません。初期値の 0 は制限なしです。

どの開始時点を選んでも、同じ投稿が同じ会話へ通知されるのは 1 回だけです。

## 設定

設定は 5 つのグループに分かれていて、AstrBot の管理パネルかプラグインページで変更できます。

**基本設定**

| 設定項目 | 初期値 | 説明 |
|---|---|---|
| `poll_interval_minutes` | 10 | チェックの間隔（最短 5 分）。1 回のチェックで、クリエイターごとに投稿一覧を 1 回だけ取得します。 |
| `max_new_posts_per_poll` | 3 | 1 回のチェックで、クリエイターごとに通知する最大件数 |
| `proxy` | 空 | FANBOX へのアクセスに使うプロキシ |

**通知開始時点**

| 設定項目 | 初期値 | 説明 |
|---|---|---|
| `start_from` | deploy | 前の節を参照 |
| `start_time` | 空 | `custom` を選んだときの開始時刻 |
| `max_post_age_hours` | 0 | 公開からこの時間数を過ぎた投稿は通知しない。0 は制限なし |

**通知スタイル**

| 設定項目 | 初期値 | 説明 |
|---|---|---|
| `push_style` | text | `text` は通知テンプレートで送信、`card` はカード添え文テンプレートでカード画像を送信。カード画像の生成に失敗したときは通知テンプレートで送ります |
| `card_text` | merge | カード画像の添え文の送り方（`card` スタイルのときのみ有効）。`merge` は添え文テンプレートの順に文章とカード画像を 1 件のメッセージにまとめ、`separate` はカード画像を境に上の文章、カード画像、下の文章を別々に送り、`none` はカード画像だけを送ります |
| `message_template` | 後述 | 通知テンプレート（`text` スタイル用）。空にすると初期値に戻ります |
| `card_template` | 後述 | カード添え文テンプレート（`card` スタイル用）。`{card_image}` を必ず 1 つ残してください。空にすると初期値に戻ります |
| `send_cover` | オン | テンプレートの `{cover_image}` を送るかどうか |
| `send_adult_cover` | オフ | R-18 の投稿でもカバー画像を送り、カード画像にも本来のカバーを表示する |
| `creator_cover_fallback` | オン | 投稿にカバー画像が設定されていないとき、クリエイターページのカバー画像を代わりに使います。FANBOX がこうした投稿を共有するときと同じ動きです。カード画像と `{cover_image}` の両方に効き、オフにするとカード画像はグレーのプレースホルダーになります |

**表示内容**（テンプレートとカード画像の両方に適用）

| 設定項目 | 初期値 | 説明 |
|---|---|---|
| `show_fee` | オン | 支援プランを表示する |
| `show_timezone` | オン | 時刻の後ろに「（北京时间）」のようなタイムゾーン名を付ける |
| `show_tags` | オン | タグを表示する |
| `show_adult_mark` | オン | R-18 マークを表示する |
| `excerpt_max_chars` | 120 | `{excerpt}` の最大文字数。0 にすると表示しない |
| `max_tags` | 6 | 表示するタグの最大数 |
| `time_format` | `%Y-%m-%d %H:%M` | `{published}` と `{updated}` の時刻の書式（strftime 形式） |
| `timezone_offset_hours` | 8 | タイムゾーン。8 は北京時間、9 は日本時間 |

**カード画像**

| 設定項目 | 初期値 | 説明 |
|---|---|---|
| `card_show_likes` | オン | 右下にいいね数を表示する |
| `card_excerpt_lines` | 2 | 抜粋の最大行数。0 にすると表示しない |
| `card_title_lines` | 2 | タイトルの最大行数 |
| `card_font_path` / `card_bold_font_path` | 空 | フォントファイルを指定する。空なら Noto Sans CJK を使います |

カード画像は幅 1430 ピクセル（Web ページを 2 倍の解像度で表示したときの大きさ）の JPEG で、サイズは 150〜400 KB ほどです。カラー絵文字は対応するフォントがないためカード画像では省かれますが、テキストメッセージ内の絵文字はそのまま送られます。

## 通知テンプレート

プラグインが出力する文章は中国語（簡体字）のため、以下のテンプレートと例の値もそのままにしています。初期テンプレートは次のとおりです。

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

### カード添え文テンプレート

通知スタイルが `card` のときに使うテンプレートです。テンプレート内の `{card_image}` はカード画像そのもので、必ず 1 つだけ残す必要があります。プラグインページのエディタでは削除できず、テンプレートにない場合は末尾に自動で追加されます。`{card_image}` より上に書いた文章はカード画像の上に、下に書いた文章はカード画像の下に表示されます。そのほかの変数や書き方は通知テンプレートと同じですが、カード画像にはすでにカバーとアイコンが入っているため、ほかの画像変数はここでは無視されます。初期テンプレートでは、カード画像の上にタイトル、下にリンクを置いています。

```
【FANBOX】{creator_name} {headline}
《{title}》
{card_image}
{post_url}
```

`card_text` が `merge` のとき、これらは QQ で 1 件のメッセージになり、タイトルが上、カード画像が中央、リンクがカード画像の下に並びます。`separate`（プラグインページでは「分开发」）のときは、カード画像を境に上の文章、カード画像、下の文章をそれぞれ 1 件ずつ送ります。`none` のときはカード画像だけを送り、テンプレートは使いません。

プラグインページでは「把卡片图移到光标处」ボタンで、テンプレート内のカード画像の位置を移動できます。

### 書き方のルール

1. `{変数}` は対応する値に置き換わります。変数名は大文字と小文字を区別します。
2. `{{` と `}}` は波かっこそのものを表します。
3. 認識できない `{xxx}` はそのまま表示され、プラグインの読み込み時にログでお知らせします。
4. 1 行の中の変数がすべて空で、ほかに文字がない行は自動で削除されます。
5. `?` で始まる行は条件付きの行です。行内の変数が 1 つでも空なら行ごと削除され、`?` 自体は表示されません。例：`?发布时间：{published}`。
6. 画像変数は、書いた位置にそのまま画像が入ります。
7. テンプレートが空のときは初期テンプレートを使います。

### テキスト変数（30 個）

例の値は 500 円プランの有料投稿で、設定はすべて初期値です。

| 変数 | 内容 | 例 |
|---|---|---|
| `{headline}` | 通知では「发布了新帖」、/fanbox最新 では「的最新帖子」 | `发布了新帖` |
| `{creator_name}` | クリエイターの名前 | `pixivFANBOX公式` |
| `{creator_id}` | クリエイター ID（ページ https://<ID>.fanbox.cc の <ID>） | `official` |
| `{creator_url}` | クリエイターページのリンク | `https://official.fanbox.cc` |
| `{creator_icon_url}` | クリエイターのアイコン画像のリンク | `https://pixiv.pximg.net/c/160x160_90_a2_g5/fanbox/public/…` |
| `{title}` | 投稿のタイトル。タイトルがないときは「（无标题）」 | `新作イラストのお知らせ` |
| `{post_id}` | 投稿 ID | `1234567` |
| `{post_url}` | 投稿のリンク | `https://official.fanbox.cc/posts/1234567` |
| `{excerpt}` | 抜粋。「抜粋の最大文字数」で切り詰めます。有料投稿にはふつう抜粋がありません | `いつも応援ありがとうございます。今月の新作です。` |
| `{excerpt_full}` | 抜粋の全文（空行を整えるだけで、切り詰めない） | `いつも応援ありがとうございます。今月の新作です。` |
| `{fee}` | プランの金額。無料投稿は 0。「支援プランを表示」の設定に関係なく入ります | `500` |
| `{fee_text}` | 「付费 · 500 日元及以上档位」または「免费公开」。「支援プランを表示」がオフなら空 | `付费 · 500 日元及以上档位` |
| `{fee_badge}` | 「500日元」または「免费」。「支援プランを表示」がオフなら空 | `500日元` |
| `{paid}` | 「付费」または「免费」。「支援プランを表示」の設定に関係なく入ります | `付费` |
| `{adult}` | R-18 の投稿なら「R-18」、それ以外は空。「R-18 マークを表示」がオフのときも空 | （空） |
| `{labels}` | プランと R-18 マークを「 · 」でつないだもの。例：「付费 · 500 日元及以上档位 · R-18」 | `付费 · 500 日元及以上档位` |
| `{restricted}` | 本文の閲覧に支援が必要なときは「需赞助」、それ以外は空 | `需赞助` |
| `{tags}` | タグを「#タグ1 #タグ2」の形で並べたもの。「タグを表示」がオフなら空 | `#イラスト #メイキング` |
| `{tags_plain}` | タグを読点でつないだもの（「タグ1、タグ2」）。「タグを表示」がオフなら空 | `イラスト、メイキング` |
| `{tag_count}` | タグの数 | `2` |
| `{published}` | 公開日時。「時刻の書式」とタイムゾーンに沿って表示し、「タイムゾーン名を表示」がオンなら後ろに「（北京时间）」が付きます | `2026-11-13 20:12（北京时间）` |
| `{published_date}` | 公開日（例：2026-11-13） | `2026-11-13` |
| `{published_time}` | 公開時刻（例：20:12） | `20:12` |
| `{published_iso}` | FANBOX の元の公開日時（日本時間の ISO 形式） | `2026-11-13T21:12:54+09:00` |
| `{updated}` | 最終更新日時。書式は published と同じ | `2026-11-14 08:30（北京时间）` |
| `{timezone}` | タイムゾーン名（例：「北京时间」）。「タイムゾーン名を表示」の設定に関係なく入ります | `北京时间` |
| `{like_count}` | いいね数 | `12` |
| `{comment_count}` | コメント数 | `3` |
| `{cover_url}` | カバー画像のリンク。投稿にカバーがないときは設定に従ってクリエイターページのカバーを使い、R-18 の投稿でカバーを送らない設定のときは空 | `https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public…` |
| `{pinned}` | 固定された投稿なら「置顶」、それ以外は空 | （空） |

### 画像変数（3 個）

| 変数 | 内容 |
|---|---|
| `{cover_image}` | カバー画像。投稿にカバーがないときは設定に従ってクリエイターページのカバーを使います。「カバー画像を添付」がオフのとき、または R-18 の投稿でカバーを送らない設定のときは送りません |
| `{card_image}` | FANBOX の Web ページ風のカード画像 |
| `{avatar_image}` | クリエイターのアイコン |

### テンプレートの例

カード画像だけを送り、その下にリンクを 1 行添える：

```
{card_image}
{post_url}
```

短く 1 行で：

```
{creator_name} 更新了《{title}》 {fee_badge} {post_url}
```

アイコンと詳しい情報：

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

## 既知の制限

投稿によってはカバー画像が設定されておらず、FANBOX の Web ページではグレーのプレースホルダーだけが表示されます。その場合、初期設定ではクリエイターページのカバー画像を代わりに使います。設定でオフにすることもできます。

1 回のチェックで見るのは、クリエイターごとに最新の 10 件だけです。2 回のチェックの間にあるクリエイターが 10 件を超えて投稿した場合、古いものは通知されません。

購読の情報は AstrBot のプラグインデータに `fanbox_subscriptions_v1` というキーで保存されます。

## 開発

```bash
python -m pytest -q tests
python -m ruff check .
python -m ruff format --check .
python -m compileall -q .
python -m json.tool _conf_schema.json
```

`fanbox_core.py`、`fanbox_api.py`、`fanbox_card.py`、`fanbox_stats.py`、`fanbox_settings.py` は AstrBot に依存しません。`fanbox_webui.py` はプラグインページのバックエンド、`pages/dashboard/` はフロントエンドです。テストには `httpx`、`pytest`、`Pillow` が必要で、Noto Sans CJK フォントがない環境ではカード画像のテストをスキップします。

## ライセンス

このプラグインは MIT ライセンスで公開しています。詳しくは [LICENSE](https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/LICENSE) をご覧ください。

</details>

<details>
<summary><b>English</b></summary>

## Overview

An [AstrBot](https://github.com/AstrBotDevs/AstrBot) plugin for following [pixivFANBOX](https://www.fanbox.cc) creators. Whenever a creator you follow publishes a new post, the plugin sends a message to the QQ group or private chat where you subscribed.

There are two push styles. The text style builds a message from a "push template", where you can combine variables freely and place images anywhere. The card style renders an image modeled on FANBOX's post cards, with the cover, avatar, name, date, plan, title, excerpt and like count. You can also add text above and below the card, for example a link to the post underneath the image.

The plugin also comes with a dashboard page where you can browse the push history, manage subscriptions, change every setting and preview pushes in real time.

By default, covers of R-18 posts are not sent. On card images the cover is replaced with "R-18 · 封面已隐藏" so that adult images don't show up in QQ groups.

## Installation

In the AstrBot dashboard, open "Plugins → Install plugin → Install from link" and enter `https://github.com/saubaka/astrbot_plugin_fanbox`. To install it manually, put this repository in AstrBot's `data/plugins/astrbot_plugin_fanbox` folder, then restart AstrBot or reload the plugin from the dashboard.

The plugin depends on `httpx` and `Pillow`, which AstrBot already ships with. Card images need a CJK font. By default the plugin uses the system's Noto Sans CJK (the package is `fonts-noto-cjk` on Debian and Ubuntu), and you can point it to other font files in the settings.

It requires AstrBot v4.26.0 or later and has been tested on aiocqhttp (OneBot v11).

## Commands

| Command | Alias | What it does |
|---|---|---|
| `/fanbox关注 <creator ID or page link>` | `fanbox_follow` | Follow this creator in the current chat |
| `/fanbox取关 <creator ID>` | `fanbox_unfollow` | Unfollow the creator in the current chat |
| `/fanbox列表` | `fanbox_list` | List the creators followed in the current chat and where each one's pushes start |
| `/fanbox最新 <creator ID>` | `fanbox_latest` | Send the creator's latest post in the current push style. Useful for previewing the style; it doesn't affect push progress |
| `/fanbox变量` | `fanbox_vars` | List every variable available in templates |
| `/fanbox检查` | `fanbox_check` | Check all subscriptions right away (admins only) |

The command names are in Chinese, so type them exactly as shown above or use the English aliases. A creator ID is the `<ID>` part of the creator's page address `https://<ID>.fanbox.cc`. You can also paste links such as `https://www.fanbox.cc/@<ID>` directly.

## Dashboard page: FANBOX 推送面板

In the AstrBot dashboard, open "Plugin pages → FANBOX 新帖推送". Use the tabs in the top left to switch sections. The "本页章节" (on this page) bar on the right jumps straight to each part of the current tab and turns into a row of buttons at the top on narrow screens. The data refreshes every 30 seconds.

The page itself is in Chinese. The table gives each tab's name followed by a translation.

| Tab | Contents |
|---|---|
| 概览 (Overview) | Pushes in the last 24 hours with an hourly trend, plus the number of followed creators, checks, a countdown to the next check, pushes in the last 7 days, errors and total pushes. Each creator gets a card showing posts pushed, check results, hourly check activity and the latest post. "预览样式" (preview style) takes you straight to the live preview. |
| 推送记录 (Push history) | Shown as FANBOX-style post cards by default. The lower-left corner of each cover tells you which chat it was sent to, which style was used and whether it was delivered. Entries are grouped by day and can be switched to a list. Recent errors are listed below. |
| 订阅 (Subscriptions) | Add a subscription by picking a group from your QQ group list, or enter a QQ number to subscribe in a private chat. Each chat has its own block where you can preview or unsubscribe. |
| 推送样式 (Push style) | Five groups of settings: push style, push template, card caption, displayed content and card image. Click a variable to insert it into a template. The live preview sits on the right, or below the settings on narrow screens. After you enter a post link (`https://<ID>.fanbox.cc/posts/<post number>`) or a creator ID, every change to the settings re-renders the preview in the new style, including unsaved changes. Each bubble in the preview is one QQ message. Below the preview you can send a test push of that message to a chosen chat or private chat; it takes two clicks to confirm. Test pushes don't advance subscription progress, aren't counted in the statistics, and are marked "测试" (test) in the push history. |
| 设置 (Settings) | Basic settings and push start point. |

Settings take effect as soon as you save them, with no restart needed. Changing the polling interval restarts the timer with the new interval right away.

To preview a specific post, the plugin pages back through the creator's post list to find it, up to 30 pages. Posts are cached for 5 minutes and images for 30 minutes, so the preview stays fast while you tweak the style.

Statistics are stored in the plugin data key `fanbox_stats_v1`. Hourly statistics are kept for 90 days, and the latest 60 pushes and 60 errors are kept, with errors dropped after 30 days at most.

AstrBot runs plugin pages inside a sandboxed iframe that can't open new windows, so links on the page are "copy link" buttons instead.

## Push start point

By default, the plugin only pushes posts published after it was deployed, and never digs up older posts.

| Start point (`start_from`) | Which posts get pushed |
|---|---|
| `deploy` (default) | Posts published after the plugin first started. Posts published after deployment but before you subscribed are pushed at the first check after subscribing, at most `max_new_posts_per_poll` at a time. |
| `subscribe` | Each subscription starts counting from the moment you subscribed. Posts published before that are never pushed. |
| `custom` | Posts published after the time in `start_time`. Write the time as `2026-11-15 08:00` to have it read in the "timezone" setting, or include the offset, as in `2026-11-15T08:00:00+09:00`. If the format is wrong, the plugin falls back to `deploy` and says so in the log. |

The time the plugin first started is stored in the plugin data key `fanbox_deployed_at` and doesn't change when you update or restart.

When `max_post_age_hours` is a positive number, posts older than that many hours aren't pushed. For example, if the bot was down for a long time, it won't flood the chat with old posts when it comes back. The default, 0, means no limit.

Whichever start point you choose, each post is pushed to the same chat only once.

## Settings

The settings come in 5 groups and can be changed in the AstrBot dashboard or on the plugin page.

**Basic settings**

| Setting | Default | Description |
|---|---|---|
| `poll_interval_minutes` | 10 | Polling interval, at least 5 minutes. Each check requests each creator's post list once. |
| `max_new_posts_per_poll` | 3 | The most posts pushed per creator in one check |
| `proxy` | empty | Proxy used to reach FANBOX |

**Push start point**

| Setting | Default | Description |
|---|---|---|
| `start_from` | deploy | See the previous section |
| `start_time` | empty | The start time when `custom` is selected |
| `max_post_age_hours` | 0 | Skip posts older than this many hours; 0 means no limit |

**Push style**

| Setting | Default | Description |
|---|---|---|
| `push_style` | text | `text` sends messages from the push template; `card` sends a card image using the card caption template, and falls back to the push template if the card can't be rendered |
| `card_text` | merge | How captions go with the card image (only for the `card` style). `merge` combines the text and the card into one message in template order, `separate` sends the text above the card, the card and the text below the card as separate messages, and `none` sends only the card |
| `message_template` | see below | Push template for the `text` style. Clear it to restore the default |
| `card_template` | see below | Card caption template for the `card` style. It must keep exactly one `{card_image}`. Clear it to restore the default |
| `send_cover` | on | Whether `{cover_image}` in templates is sent |
| `send_adult_cover` | off | Send covers for R-18 posts too, and show the real cover on card images |
| `creator_cover_fallback` | on | When a post has no cover, use the creator page's cover instead, the same image FANBOX uses when sharing such posts. Applies to both card images and `{cover_image}`; when turned off, the card shows a gray placeholder |

**Displayed content** (applies to both templates and card images)

| Setting | Default | Description |
|---|---|---|
| `show_fee` | on | Show the paid plan |
| `show_timezone` | on | Add a timezone name such as "（北京时间）" after times |
| `show_tags` | on | Show tags |
| `show_adult_mark` | on | Show the R-18 mark |
| `excerpt_max_chars` | 120 | Maximum length of `{excerpt}`; 0 hides it |
| `max_tags` | 6 | The most tags to show |
| `time_format` | `%Y-%m-%d %H:%M` | Time format for `{published}` and `{updated}` (strftime syntax) |
| `timezone_offset_hours` | 8 | Timezone offset: 8 is Beijing time, 9 is Japan time |

**Card image**

| Setting | Default | Description |
|---|---|---|
| `card_show_likes` | on | Show the like count in the lower right |
| `card_excerpt_lines` | 2 | Maximum lines of excerpt; 0 hides it |
| `card_title_lines` | 2 | Maximum lines of title |
| `card_font_path` / `card_bold_font_path` | empty | Custom font files; Noto Sans CJK is used when empty |

Card images are 1430 pixels wide (the size of the web page on a 2x display), saved as JPEG at roughly 150 to 400 KB. Color emoji have no matching font and are left out of card images; emoji in text messages are unaffected.

## Push template

The plugin's output text is in Simplified Chinese, so the templates and sample values below are left as they are. The default template is:

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

### Card caption template

This template is used when the push style is `card`. The `{card_image}` in it is the card image itself: it has to stay, and there can only be one. The editor on the plugin page won't let you delete it, and if a template is missing it, the plugin adds it at the end. Text written above `{card_image}` appears above the card, and text written below it appears below the card. Other variables and rules work the same as in the push template, but other image variables are ignored here, since the card already contains the cover and avatar. The default template puts the title above the card and the link below it:

```
【FANBOX】{creator_name} {headline}
《{title}》
{card_image}
{post_url}
```

With `card_text` set to `merge`, all of this is one QQ message: the title on top, the card in the middle and the link under the card. With `separate` (called "分开发" on the plugin page), the message is split at the card, and the text above, the card and the text below are sent one by one. With `none`, only the card is sent and the template isn't used.

On the plugin page, the "把卡片图移到光标处" (move card to cursor) button moves the card to a different spot in the template.

### Template rules

1. `{variable}` is replaced with its value. Variable names are case-sensitive.
2. `{{` and `}}` stand for literal braces.
3. An unknown `{xxx}` is shown as is, and the plugin mentions it in the log when it loads.
4. A line whose variables are all empty and that has no other text is removed automatically.
5. A line starting with `?` is conditional: if any variable in it is empty, the whole line is removed. The `?` itself is never shown, for example `?发布时间：{published}`.
6. An image variable puts the image exactly where you write it in the message.
7. An empty template means the default template is used.

### Text variables (30)

The sample values come from a paid post on the 500 yen plan, with every setting at its default.

| Variable | Meaning | Sample value |
|---|---|---|
| `{headline}` | "发布了新帖" (posted something new) for pushes, "的最新帖子" (latest post) for /fanbox最新 | `发布了新帖` |
| `{creator_name}` | Creator's display name | `pixivFANBOX公式` |
| `{creator_id}` | Creator ID, the <ID> in the page address https://<ID>.fanbox.cc | `official` |
| `{creator_url}` | Link to the creator's page | `https://official.fanbox.cc` |
| `{creator_icon_url}` | Link to the creator's avatar image | `https://pixiv.pximg.net/c/160x160_90_a2_g5/fanbox/public/…` |
| `{title}` | Post title, or "（无标题）" (untitled) when there is none | `新作イラストのお知らせ` |
| `{post_id}` | Post ID | `1234567` |
| `{post_url}` | Link to the post | `https://official.fanbox.cc/posts/1234567` |
| `{excerpt}` | Excerpt, cut to the "maximum excerpt length" setting; paid posts usually have no excerpt | `いつも応援ありがとうございます。今月の新作です。` |
| `{excerpt_full}` | The full excerpt, with blank lines tidied but nothing cut | `いつも応援ありがとうございます。今月の新作です。` |
| `{fee}` | Plan amount, 0 for free posts; not affected by "show the paid plan" | `500` |
| `{fee_text}` | "付费 · 500 日元及以上档位" (paid, 500 yen plan and above) or "免费公开" (free); empty when "show the paid plan" is off | `付费 · 500 日元及以上档位` |
| `{fee_badge}` | "500日元" or "免费" (free); empty when "show the paid plan" is off | `500日元` |
| `{paid}` | "付费" (paid) or "免费" (free); not affected by "show the paid plan" | `付费` |
| `{adult}` | "R-18" for R-18 posts, otherwise empty; also empty when "show the R-18 mark" is off | (empty) |
| `{labels}` | Plan and R-18 mark joined with " · ", for example "付费 · 500 日元及以上档位 · R-18" | `付费 · 500 日元及以上档位` |
| `{restricted}` | "需赞助" (support required) when the post body needs a paid plan, otherwise empty | `需赞助` |
| `{tags}` | Tags written as "#tag1 #tag2"; empty when "show tags" is off | `#イラスト #メイキング` |
| `{tags_plain}` | Tags joined as "tag1、tag2"; empty when "show tags" is off | `イラスト、メイキング` |
| `{tag_count}` | Number of tags | `2` |
| `{published}` | Publication time in the "time format" and timezone, followed by "（北京时间）" when "show the timezone" is on | `2026-11-13 20:12（北京时间）` |
| `{published_date}` | Publication date, such as 2026-11-13 | `2026-11-13` |
| `{published_time}` | Publication time of day, such as 20:12 | `20:12` |
| `{published_iso}` | FANBOX's original publication time, in ISO format in Japan time | `2026-11-13T21:12:54+09:00` |
| `{updated}` | Last update time, in the same format as published | `2026-11-14 08:30（北京时间）` |
| `{timezone}` | Timezone name, such as "北京时间" (Beijing time); not affected by "show the timezone" | `北京时间` |
| `{like_count}` | Number of likes | `12` |
| `{comment_count}` | Number of comments | `3` |
| `{cover_url}` | Link to the cover image. When the post has no cover, the creator page's cover is used depending on the setting; empty for R-18 posts when their covers aren't allowed | `https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public…` |
| `{pinned}` | "置顶" (pinned) for pinned posts, otherwise empty | (empty) |

### Image variables (3)

| Variable | Meaning |
|---|---|
| `{cover_image}` | Cover image. When the post has no cover, the creator page's cover is used depending on the setting. Not sent when "attach cover" is off, or for R-18 posts when their covers aren't allowed |
| `{card_image}` | Card image styled after FANBOX's web page |
| `{avatar_image}` | Creator's avatar |

### Template examples

Only the card, with a link underneath:

```
{card_image}
{post_url}
```

A short one-liner:

```
{creator_name} 更新了《{title}》 {fee_badge} {post_url}
```

Avatar plus details:

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

## Known limitations

Some posts have no cover, and FANBOX's web page shows only a gray placeholder for them. In that case the plugin uses the creator page's cover by default; you can turn this off in the settings.

Each check only looks at the 10 latest posts of each creator. If a creator publishes more than 10 posts between two checks, the older ones won't be pushed.

Subscriptions are stored in AstrBot's plugin data under the key `fanbox_subscriptions_v1`.

## Development

```bash
python -m pytest -q tests
python -m ruff check .
python -m ruff format --check .
python -m compileall -q .
python -m json.tool _conf_schema.json
```

`fanbox_core.py`, `fanbox_api.py`, `fanbox_card.py`, `fanbox_stats.py` and `fanbox_settings.py` don't depend on AstrBot. `fanbox_webui.py` is the plugin page's backend and `pages/dashboard/` is its frontend. The tests need `httpx`, `pytest` and `Pillow`; card tests are skipped when the Noto Sans CJK font isn't available.

## License

This plugin is released under the MIT License. See [LICENSE](https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/LICENSE) for details.

</details>
