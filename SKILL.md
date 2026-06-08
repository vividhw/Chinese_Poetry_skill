---
name: chinese-poetry
description: >
  中国古典诗词数据库检索。用于搜索唐诗、宋词、元曲、诗经、楚辞、论语等古典文集，
  按作者、标题、内容、朝代、体裁检索，或在检索真实作品后模仿特定诗人/朝代风格创作诗词。
  数据集来自 chinese-poetry/chinese-poetry（5.5万首唐诗、26万首宋诗、2.1万首宋词）。
compatibility:
  requires:
    - git（克隆数据集时需要）
    - bash、grep、sed、awk（均为系统内置）
---

# Chinese Poetry Skill — 中国古典诗词检索与创作

基于 [chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) 数据集（~345 MB JSON），按需检索，绝不全量加载。

---

## 数据集路径

搜索前先确定数据集位置，按优先级检测：

1. 用户本地已有路径（如 `D:\github\chinese-poetry-master\chinese-poetry-master`）
2. 用户通过环境变量 `CHINESE_POETRY_PATH` 指定的路径
3. Skill 缓存目录 `~/.claude/chinese-poetry-cache/`（自动 clone）

**若三个路径都不存在，执行 clone：**

```bash
git clone --depth 1 https://github.com/chinese-poetry/chinese-poetry.git ~/.claude/chinese-poetry-cache/
```

确定路径后，后续所有搜索都基于该路径（记为 `$CP`）。

---

## 目录结构与字段映射

**不同目录的 JSON 字段名不同，搜索时必须区分！**

| 目录 | 体裁 | 诗句字段 | 标题字段 | 特有字段 |
|------|------|----------|----------|----------|
| `全唐诗/` | 唐诗、宋诗 | `paragraphs` | `title` | `id` |
| `宋词/` | 宋词 | `paragraphs` | — | `rhythmic`（词牌名） |
| `元曲/` | 元曲 | `paragraphs` | `title` | `dynasty` |
| `诗经/` | 诗经 | `content` | `title` | `chapter`, `section` |
| `楚辞/` | 楚辞 | `content` | `title` | `section`, `author` |
| `纳兰性德/` | 纳兰词 | `para` | `title` | — |
| `论语/` | 论语 | — | `chapter` | `paragraphs` |
| `蒙学/` | 蒙学 | 各文件不同 | 各文件不同 | — |
| `四书五经/` | 四书五经 | 各文件不同 | 各文件不同 | — |
| `五代诗词/` | 花间集、南唐词 | `paragraphs` | `title` | — |
| `曹操诗集/` | 曹操诗 | `paragraphs` | `title` | — |
| `水墨唐诗/` | 唐诗 | `paragraphs` | `title` | — |

**关键差异：**
- 诗句内容字段有 `paragraphs` / `content` / `para` 三种
- 宋词用 `rhythmic`（词牌名）标识，常无 `title`
- 诗经/楚辞用 `content` 数组存诗句，而非 `paragraphs`

---

## 关键提示：JSON 格式中冒号后有空格

**所有 JSON 文件的键值对都是 `"key": "value"` 格式（冒号后有空格）。** grep 时必须写出空格：

```bash
# 错误：不会匹配
grep -rn '"author":"李白"' ...

# 正确：冒号后有空格
grep -rn '"author": "李白"' ...
```

---

## 搜索命令

所有搜索一律用 `grep` + `find` 在 JSON 文件上执行，**只返回命中行**，严禁读取整个文件。

### 1. 按作者搜索

```bash
grep -rn '"author": "<作者名>"' "$CP/<目录>/" | head -30
```

若结果较多，用 `head -20` 限制。诗经无 `author` 字段，跳过。

### 2. 按标题搜索（模糊匹配）

```bash
grep -rn '"title": "[^"]*<标题关键词>[^"]*"' "$CP/<目录>/" | head -20
```

宋词目录优先用 `rhythmic` 搜索词牌名：
```bash
grep -rn '"rhythmic": "<词牌名>"' "$CP/宋词/" | head -20
```

### 3. 按内容关键词搜索

```bash
grep -rn '<关键词>' "$CP/<目录>/" | head -30
```

目录明确时缩小范围。关键词会命中 `paragraphs`、`content`、`para`、`title` 等字段。

### 4. 从搜索结果中提取完整一首诗词

grep 返回单行，但一首诗词跨多行。命中的行号后，用 `Read` 工具读取命中行前后各 5-10 行来获取完整诗词。

### 5. 按体裁列举

先确定目录，再用 `ls` 看文件列表，然后按需搜索。小文件（<200KB）如诗经、楚辞、纳兰性德，可直接 `Read` 全文。

---

## 返回结果处理

### JSON 结构说明（因目录而异）

**全唐诗 / 宋词 / 元曲：**
```json
{
  "author": "李白",
  "title": "静夜思",
  "paragraphs": ["床前明月光，", "疑是地上霜。", ...]
}
```

**诗经 / 楚辞（用 `content` 而非 `paragraphs`）：**
```json
{
  "title": "关雎",
  "chapter": "国风",
  "section": "周南",
  "content": ["关关雎鸠，在河之洲。", ...]
}
```

**纳兰性德（用 `para` 而非 `paragraphs`）：**
```json
{
  "author": "纳兰性德",
  "title": "长相思·山一程",
  "para": ["山一程，水一程，..."]
}
```

**宋词特有 `rhythmic`（词牌名）字段，常无 `title`。**

### 展示格式

多首结果时，每条展示如下：

```
《标题》 — 作者

诗句内容（每行一句）

---
体裁：xxx
```

最多一次展示 5 首，用户要求更多时继续。

---

## 风格模仿创作

当用户要求"模仿李白风格写一首诗"或"写一首纳兰性德风格的词"时：

### 必须先检索再创作

1. 按作者搜索，检索该作者 **3-5 首代表作**（用 grep 抽取）
2. 用 `Read` 读取命中区域的完整诗词内容（前后各 5-10 行）
3. 分析风格：常用意象、句式特点、情感基调
4. 基于分析结果进行创作
5. 创作后标注参考了哪些原作

### 输出格式

```
## 风格分析
- 意象：xxx
- 句式：xxx
- 情感：xxx

## 创作
（新作）

---
参考原作：
1. 《xxx》
2. 《xxx》
```

---

## 核心规则

1. **绝不全量读取** — 任何情况下都不要 cat 超过 50KB 的文件到上下文
2. **先搜后读** — 用 grep 定位后再 Read 局部内容，不要一次性读取整个文件
3. **结果限制** — 每次最多展示 5 首，除非用户明确要求更多
4. **路径容错** — 如果路径不存在，自动 clone 数据集
5. **中文编码** — JSON 文件为 UTF-8，grep 结果中的中文正常展示
6. **先检索再创作** — 用户要求写诗时，必须先检索相关诗人的原作作为参考，不可凭空创作

---

## 常用速查

| 需求 | 命令模板 |
|------|---------|
| 搜索李白（唐诗） | `grep -rn '"author": "李白"' "$CP/全唐诗/" \| head -30` |
| 搜索苏轼（宋词） | `grep -rn '"author": "苏轼"' "$CP/宋词/" \| head -30` |
| 含"明月"的诗句 | `grep -rn '明月' "$CP/全唐诗/" \| head -20` |
| 搜索词牌名 | `grep -rn '"rhythmic": "水调歌头"' "$CP/宋词/" \| head -20` |
| 搜索关汉卿元曲 | `grep -rn '"author": "关汉卿"' "$CP/元曲/" \| head -30` |
| 读取诗经某篇 | grep 定位行号后 `Read "$CP/诗经/shijing.json"` 指定行范围 |
| 读取楚辞某篇 | grep 定位行号后 `Read "$CP/楚辞/chuci.json"` 指定行范围 |
| 搜索纳兰词 | `grep -rn '纳兰性德\|人生若只' "$CP/纳兰性德/" \| head -20` |
| 随机获取诗 | `find "$CP/全唐诗/" -name "*.json" \| shuf -n 1 \| xargs head -c 3000` |
| 统计某诗人作品数 | `grep -rc '"author": "<人名>"' "$CP/<目录>/" \| awk -F: '{s+=$2}END{print s}'` |
