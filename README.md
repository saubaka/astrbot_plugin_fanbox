# FANBOX 新帖推送（astrbot_plugin_fanbox）

[AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。订阅 [pixivFANBOX](https://www.fanbox.cc) 创作者，有新帖时推送到订阅时所在的群聊或私聊。

推送有两种样式：

- **text**：按"推送模板"拼消息。模板里用 `{变量}` 完全自定义，图片也能插在任意位置。
- **card**：只发一张仿 FANBOX 网页帖子卡片的图片，包括封面、头像、名字、日期、档位、标题、摘要和点赞数。图片用 Pillow 在本地渲染，不经过外部服务。

**只读取 FANBOX 公开的帖子列表**（`api.fanbox.cc/post.listCreator`），**不登录**，不需要任何 cookie。拿不到付费正文和帖子内的图片，也不会转发它们。封面、摘要和点赞数是 FANBOX 对所有人公开展示的内容；付费帖在未登录时摘要通常为空。

R-18 帖子默认不发封面。卡片图里的封面会换成"R-18 · 封面已隐藏"，避免在 QQ 群里发出成人图片。

## 安装

- **从链接安装**：在 AstrBot 管理面板 → 插件 → 安装插件 → 从链接安装，填 `https://github.com/saubaka/astrbot_plugin_fanbox`。
- **手动安装**：把本仓库放到 AstrBot 的 `data/plugins/astrbot_plugin_fanbox`，然后重启 AstrBot，或在面板里重载插件。

**依赖**：`httpx`、`Pillow`，AstrBot 自带。卡片图需要中日文字体，默认找系统里的 Noto Sans CJK（Debian/Ubuntu 的包名是 `fonts-noto-cjk`），也可以在配置里指定字体文件。

**平台**：在 aiocqhttp（OneBot v11）上测试过。

## 指令

| 指令 | 别名 | 作用 |
|---|---|---|
| `/fanbox关注 <创作者ID或主页链接>` | `fanbox_follow` | 订阅到当前会话 |
| `/fanbox取关 <创作者ID>` | `fanbox_unfollow` | 取消当前会话的订阅 |
| `/fanbox列表` | `fanbox_list` | 当前会话订阅了谁，以及推送起点 |
| `/fanbox最新 <创作者ID>` | `fanbox_latest` | 按当前推送样式发最新一篇，用来预览样式，不影响推送进度 |
| `/fanbox变量` | `fanbox_vars` | 列出模板里能用的全部变量 |
| `/fanbox检查` | `fanbox_check` | （管理员）立即检查一次全部订阅 |

创作者 ID 就是主页 `https://<ID>.fanbox.cc` 里的 `<ID>`。也可以直接粘贴 `https://www.fanbox.cc/@<ID>` 这类链接。

## 插件页：FANBOX 推送面板

在 AstrBot 管理面板 → 插件 → FANBOX 新帖推送里，打开插件页「FANBOX 推送面板」。界面每 30 秒自动刷新，数字原地滚动更新。

| 区域 | 内容 |
|---|---|
| 概览 | 近 24 小时推送数和每小时趋势线；订阅创作者、近 24 小时检查、下次检查倒计时、近 7 天推送、近 24 小时报错、总推送 |
| 创作者 | 每位创作者一张卡片，包括：<br>· 推送篇数（1 小时 / 24 小时 / 7 天 / 总计）<br>· 近 24 小时检查结果（成功 / 未找到 / 被拦截 / 出错）<br>· 每小时检查柱状图（有推送的小时会高亮）<br>· 最新帖子（封面、标题、档位、点赞）<br>· 订阅它的会话，可以预览或取消订阅 |
| 添加订阅 / 立即检查 | 选择 QQ 群（通过 OneBot 的 `get_group_list` 读取）或填写 QQ 号即可订阅；"立即检查"等于发一次 `/fanbox检查` |
| 推送记录 | 最近推送的帖子、推到了哪个会话、用的什么样式、是否送达 |
| 最近报错 | 被拦截、获取失败、发送失败、卡片渲染失败、图片下载失败，附原因和插件的处理结果 |
| 设置 | 按配置文件的定义列出全部配置项，开关、数字、选项、文字各用合适的控件。<br>推送模板有编辑器：33 个变量一点就能插入。<br>还有实时预览，会用最新一篇帖子和还没保存的修改生成实际消息。<br>保存后立即生效，不用重启；改轮询间隔会马上按新间隔重新计时。 |

- 统计数据存在插件 KV 的 `fanbox_stats_v1` 里。按小时统计保留 90 天；推送记录和报错各保留最近 60 条，报错最多保留 30 天。
- 页面不加载任何外部脚本或字体。头像和封面直接从 `pixiv.pximg.net` 加载，请求时不带 Referer。

## 推送起点

**默认只推送插件部署之后发布的帖子**，不会把以前的帖子翻出来推送。

| 起点（`start_from`） | 推送哪些帖子 |
|---|---|
| `deploy`（默认） | 插件第一次启动之后发布的帖子。部署后、订阅前发布的帖子，订阅后的下一次检查时会补推（每次最多推 `max_new_posts_per_poll` 篇）。 |
| `subscribe` | 每个订阅各自从订阅那一刻开始，订阅前已经发布的帖子都不推送 |
| `custom` | `start_time` 填写的时间之后发布的帖子。时间写成 `2026-11-15 08:00`，按"时区"配置理解；也可以写带时区的 `2026-11-15T08:00:00+09:00`。填不对时退回 `deploy`，日志里会提示。 |

- "插件第一次启动的时间"记在插件 KV 的 `fanbox_deployed_at` 里，之后升级、重启都不会改变。
- `max_post_age_hours` 填正数时，发布超过这么多小时的帖子不推送。比如机器人停了很久再恢复，不会补推一堆旧帖。默认 0，表示不限制。
- 不管选哪种起点，同一篇帖子在同一个会话里只推送一次。

## 配置

配置分 5 组，在 AstrBot 面板里修改。

**基础设置**

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `poll_interval_minutes` | 10 | 轮询间隔，最小 5 分钟。每次每个创作者只请求一次列表。 |
| `max_new_posts_per_poll` | 3 | 每个创作者每次最多推几篇 |
| `proxy` | 空 | 访问 FANBOX 用的代理 |

**推送起点**

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `start_from` | deploy | 见上一节 |
| `start_time` | 空 | `custom` 时的起点时间 |
| `max_post_age_hours` | 0 | 不推送发布超过几小时的帖子，0 表示不限制 |

**推送样式**

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `push_style` | text | `text` 按模板发；`card` 只发卡片图，渲染失败时自动改发文字模板 |
| `message_template` | 见下 | 推送模板，清空即恢复默认 |
| `send_cover` | 开 | 控制模板里的 `{cover_image}` |
| `send_adult_cover` | 关 | R-18 帖子也发封面，卡片里也显示真封面 |

**显示内容**（同时作用于模板和卡片图）

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `show_fee` | 开 | 显示付费档位 |
| `show_timezone` | 开 | 时间后面带"（北京时间）"这样的时区名 |
| `show_tags` | 开 | 显示标签 |
| `show_adult_mark` | 开 | 显示 R-18 标记 |
| `excerpt_max_chars` | 120 | `{excerpt}` 的长度，填 0 不显示 |
| `max_tags` | 6 | 最多几个标签 |
| `time_format` | `%Y-%m-%d %H:%M` | `{published}`、`{updated}` 的 strftime 格式 |
| `timezone_offset_hours` | 8 | 8 = 北京时间，9 = 日本时间 |

**卡片图**

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `card_show_likes` | 开 | 右下角点赞数 |
| `card_excerpt_lines` | 2 | 摘要最多几行，填 0 不显示 |
| `card_title_lines` | 2 | 标题最多几行 |
| `card_font_path` / `card_bold_font_path` | 空 | 自定义字体文件，留空用 Noto Sans CJK |

卡片宽 1430 像素（相当于网页在 2 倍屏下的尺寸），JPEG 格式，大约 150–400 KB。彩色 emoji 没有对应字体，卡片里会省略；文字消息里的 emoji 不受影响。

## 推送模板

默认模板：

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

### 写法规则

1. `{变量}` 会被替换成对应的值，变量名区分大小写。
2. `{{` 和 `}}` 表示花括号本身。
3. 不认识的 `{xxx}` 会原样显示，插件加载时日志里会提示。
4. 一行里的变量全为空、这一行又没有其他文字时，整行自动删掉。
5. 以 `?` 开头的行是条件行：只要行里有一个变量为空，整行就删掉，`?` 本身不显示。例如 `?发布时间：{published}`。
6. 图片变量写在哪儿，图片就出现在消息的哪个位置。
7. 模板清空时使用默认模板。

### 文字变量（30 个）

示例值来自一篇 500 日元档的付费帖，配置全为默认值。

| 变量 | 含义 | 示例值 |
|---|---|---|
| `{headline}` | 推送时是“发布了新帖”，/fanbox最新 时是“的最新帖子” | `发布了新帖` |
| `{creator_name}` | 创作者昵称 | `pixivFANBOX公式` |
| `{creator_id}` | 创作者 ID，也就是主页 https://<ID>.fanbox.cc 里的 <ID> | `official` |
| `{creator_url}` | 创作者主页链接 | `https://official.fanbox.cc` |
| `{creator_icon_url}` | 创作者头像图片链接 | `https://pixiv.pximg.net/c/160x160_90_a2_g5/fanbox/public/…` |
| `{title}` | 帖子标题（没有标题时是“（无标题）”） | `新作イラストのお知らせ` |
| `{post_id}` | 帖子 ID | `1234567` |
| `{post_url}` | 帖子链接 | `https://official.fanbox.cc/posts/1234567` |
| `{excerpt}` | 摘要，按“摘要最多显示多少字”截断；付费帖未登录时通常为空 | `いつも応援ありがとうございます。今月の新作です。` |
| `{excerpt_full}` | 完整摘要（只整理空行，不截断） | `いつも応援ありがとうございます。今月の新作です。` |
| `{fee}` | 档位金额数字，免费帖是 0（不受“显示付费档位”影响） | `500` |
| `{fee_text}` | “付费 · 500 日元及以上档位”或“免费公开”；关闭“显示付费档位”时为空 | `付费 · 500 日元及以上档位` |
| `{fee_badge}` | “500日元”或“免费”；关闭“显示付费档位”时为空 | `500日元` |
| `{paid}` | “付费”或“免费”（不受“显示付费档位”影响） | `付费` |
| `{adult}` | R-18 帖子是“R-18”，否则为空；关闭“显示 R-18 标记”时为空 | （空） |
| `{labels}` | 档位和 R-18 用“ · ”连起来，例如“付费 · 500 日元及以上档位 · R-18” | `付费 · 500 日元及以上档位` |
| `{restricted}` | 未登录看不了正文时是“需赞助”，否则为空 | `需赞助` |
| `{tags}` | 标签，写成“#标签1 #标签2”；关闭“显示标签”时为空 | `#イラスト #メイキング` |
| `{tags_plain}` | 标签，用顿号连接“标签1、标签2”；关闭“显示标签”时为空 | `イラスト、メイキング` |
| `{tag_count}` | 标签个数 | `2` |
| `{published}` | 发布时间，按“时间格式”和时区；开启“显示时区”时后面带“（北京时间）” | `2026-11-13 20:12（北京时间）` |
| `{published_date}` | 发布日期，例如 2026-11-13 | `2026-11-13` |
| `{published_time}` | 发布时刻，例如 20:12 | `20:12` |
| `{published_iso}` | FANBOX 原始发布时间（日本时间 ISO 格式） | `2026-11-13T21:12:54+09:00` |
| `{updated}` | 最后更新时间，格式同 published | `2026-11-14 08:30（北京时间）` |
| `{timezone}` | 时区名称，例如“北京时间”（不受“显示时区”影响） | `北京时间` |
| `{like_count}` | 点赞数 | `12` |
| `{comment_count}` | 评论数 | `3` |
| `{cover_url}` | 封面图链接（R-18 帖子在不允许发封面时为空） | `https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public…` |
| `{pinned}` | 置顶帖是“置顶”，否则为空 | （空） |

### 图片变量（3 个）

| 变量 | 含义 |
|---|---|
| `{cover_image}` | 封面图（关闭“附带封面图”，或 R-18 帖子不允许发封面时不发） |
| `{card_image}` | 仿 FANBOX 网页样式的卡片图 |
| `{avatar_image}` | 创作者头像 |

### 模板示例

只发卡片图，下面加一行链接：

```
{card_image}
{post_url}
```

简短的一行：

```
{creator_name} 更新了《{title}》 {fee_badge} {post_url}
```

头像加详细信息：

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

- FANBOX 会拦截 Cloudflare Workers 的请求。在机房 IP 上，"单帖详情"接口（`post.info`）也会被拦。所以本插件只用帖子列表接口，这个接口在一般服务器上可以正常访问。
- 每次只看每个创作者最新的 10 篇。两次检查之间某位创作者发了超过 10 篇时，更早的几篇不会推送。
- 订阅记录存在 AstrBot 的插件 KV 里，键名 `fanbox_subscriptions_v1`。

## 开发

```bash
python -m pytest -q tests
python -m ruff check .
python -m ruff format --check .
python -m compileall -q .
python -m json.tool _conf_schema.json
```

`fanbox_core.py`、`fanbox_api.py`、`fanbox_card.py`、`fanbox_stats.py`、`fanbox_settings.py` 不依赖 AstrBot；`fanbox_webui.py` 是插件页的后端接口，`pages/dashboard/` 是前端。测试需要 `httpx`、`pytest`、`Pillow`；没有 Noto Sans CJK 字体时，卡片测试会跳过。
