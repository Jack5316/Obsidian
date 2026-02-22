---
title: "从消费到创造，Obsidian 如何成为你的信息管理基地？ ｜Digital Explorer#043"
source: "https://next.iois.me/digital-explorer-043/"
author:
  - "[[赵赛坡]]"
published: 2024-10-16
created: 2026-02-22
description: "Dailyio 对话服务 ChatIO 迎来重要更新。"
tags:
  - "clippings"
---
## Editor’s Note

今天是 2024 年 10 月 16 日，您正在阅读的是第 43 期 。

作为一个常年和信息打交道的内容生产者，我如何从信息的消费、加工、创造等环节，逐步构建起一个高效的信息管理基地？本期将带来详细的流程分享与使用思考，这背后既有传统的工具的「功劳」，还有各类大模型的支持。

与此同时， **Dailyio 对话服务 ChatIO 重要更新** 、OpenRouter 上有哪些值得尝试的免费模型、Gemini 更新等也是本周应用部分关注的议题。

本期为会员免费内容，欢迎成为 [Dailyio 付费会员](https://next.iois.me/membership/) 获取更多专属邮件通讯。接下来，欢迎和我一起探索关于大模型使用的所有可能。

---

## 大模型·流程

### 从消费到创造，Obsidian 如何成为你的信息管理基地？

笔记工具 Obsidian 早已名声在外，不用过多介绍。它是典型的「本地优先」笔记工具，原生支持 MarkDown、横跨多个平台、拥有丰富的插件体系，每个用户都可以根据实际需求，定制属于自己的 Obsidian 使用流程。

本期来聊聊作为一个常年和信息打交道的内容生产者，我如何从信息的消费、加工、创造等环节，逐步构建起一个高效的信息管理基地，这背后既有传统的工具的「功劳」，还有各类大模型的支持。

这个流程的第一步，就是如何让 Obsidian 成为「稍后读应用」？

**把网页内容快速存储到 Obsidian**

把网页内容存储到 Obsidian 的方法有很多，最简单的莫过于复制粘贴，在「设置/编辑器」里找到「高级」，勾选「自动转换 HTML」即可实现复制网页内容并解析为 Markdown 格式文本的功能：

![img](https://oss.dailyio.info/dailyio/2024/10/5c46fb81b3d5fdd7b018831a86bb6c34.webp)

这个方法有时候并不好用，比如我们要将整个页面内容存储过来的时候，复制、粘贴的操作就显得非常笨重。

推荐几个其他的方法，如果你和我一样使用基于 Chromium 引擎的浏览器（包括 Chrome、Edge、Brave），那么可以试试这款 [浏览器扩展](https://chromewebstore.google.com/detail/markdownload-markdown-web/pcmpcfapbekmbjjkdalcgopdkipoggdi?ref=next.iois.me) ，利用 Obsidian 的 [Advanced URI 插件](https://publish.obsidian.md/advanced-uri-doc/Home?ref=next.iois.me) ，可以一键将网页发送到 Obsidian 的特定文件夹，非常简单：

![img](https://oss.dailyio.info/dailyio/2024/10/cc7c20d31e1ac595d88c9961190aa1dd.webp)

设置完成后，任意页面打开右键菜单，在 「MarkDownload」的功能项里选择「Send Tab to Obsidian」即可：

![img](https://oss.dailyio.info/dailyio/2024/10/fcc2ff84f0e496fb536bb594447b5d5b.webp)

第二个方法是使用 Obsidian 官方的免费的浏览器扩展「 [Obsidian Web Clipper](https://chromewebstore.google.com/detail/obsidian-web-clipper/akiokmdijehkppdjnfdhdgcoeehpbfgd?hl=en&ref=next.iois.me) 」，仅限于将网页发送到 Obsidian，如果你还有其他网页存档的需求，或许 MarkDownload 更值得尝试。

但「Obsidian Web Clipper」有一个「杀手级的功能」： [支持 iOS 的 Safari](https://apps.apple.com/gb/app/obsidian-web-clipper/id6720708363?ref=next.iois.me) 。如下图所示，在任意页面，调出浏览器扩展，选择「Obsidian Web Clipper」，可自定义诸如标题、标签等内容，然后「Add to Obsidian」：

![img](https://oss.dailyio.info/dailyio/2024/10/c633f626af8f84016161881155a9c447.webp)

我之前在 iPhone 一直使用一个「复古」的方案：Obsidian 的 CEO Kepano 做了个 JS 小书签，用来把文章剪切到 Obsidian 里。操作比较简单，代码开源，感兴趣的朋友可以在 [这里](https://gist.github.com/kepano/90c05f162c37cf730abb8ff027987ca3?ref=next.iois.me) 查看或定制。

无论用哪种方法，现在你的 Obsidian 已经有了「稍后读」应用的属性，接下来，我们开始消费。

**引入大模型，提升信息消费效率**

下图是我现在使用 Obsidian 的场景，左侧是剪辑的文章，右边是一个对话框口，调用大模型（图示里的是 Gemini 1.5 Pro）快速进行对话：

![img](https://oss.dailyio.info/dailyio/2024/10/e18e696fdce40c7711c6e60c00fcfeb0.webp)

整个操作使用了 [Obsidian 插件 Copilot](https://github.com/logancyang/obsidian-copilot?ref=next.iois.me) ，该插件允许用户调用诸如 OpenAI、Gemini 等大模型的能力，并支持第三方兼容 OpenAI API 格式的调用，同时提供了三个不同的对话方式：

- Chat：最基础的对话功能，可利用快速插入某条笔记的方式实现精准的上下文对话；
- Long Q&A：这个模式使用当前活动笔记作为上下文，比如上图左侧的笔记，相对于 Chat 模式更聚焦；
- Vault QA：这个模式使用你的整个笔记库作为上下文，但我并不推荐，一来处理速度慢，二来笔记里的一些私密信息可能会被大模型「学习」。

三种模式里，我更推荐「Long Q&A」，它让我们将焦点放在特定笔记里，通过对话的形式，快速获取摘录信息的主要内容，并使用大模型进行延伸思考，Copilot 内置了一些基本的提示，如下图所示：

![img](https://oss.dailyio.info/dailyio/2024/10/3bcf08a36cfeb6ab306ef9caf134df8e.webp)

用户还可以自定义提示，然后使用「/」即可快速调出自定义的提示，而在大模型生成内容之后，我们还可以一键将其插入到笔记的顶部，非常方便：

![img](https://oss.dailyio.info/dailyio/2024/10/8b39baa4265d45c7756a58c6b2091bb4.webp)

**为意识流的日记引入大模型整理专家**

很多朋友会将「每日日记」作为使用 Obsidian 的重要方式，每天打开一则空白笔记，然后无压力地记录一些想法、摘录等，还能借助 Obsidian 的链接机制，将其他内容串连在一起。

我也是这类用户。这类方法的确减轻了记录的压力，但我发现，压力转移到了「整理」阶段，因为文本里存在大量混乱的想法与摘录，而且每天的记录习惯或方式也不相同，这导致仅仅依靠所谓「格式化」并不能完全解决问题。

那么大模型能否解决这个问题？就像上一小节我们处理收集的网页素材一样，我们同样也可以将一则日记作为一个「上下文」，然后构建一个提示词，让大模型快速整理一则笔记的内容，下面是一个提示词示例：

![img](https://oss.dailyio.info/dailyio/2024/10/6afa9dd3ba7e719ac203aace2363e0ab.webp)

我会在每天晚上调用这个提示，并将大模型生成的内容插入日记内容的顶部，测试了一段时间之后效果不错。

这样格式化的内容不仅能够降低整理杂乱笔记的压力，还能大幅提升回顾的效率，不管是第二天回顾还是一周之后的回顾，我只需查看日记顶部的整理就能快速完成整个流程了。

**笔记条目越来越多，让大模型帮你发现联系**

「 [Smart Connections](https://github.com/brianpetro/obsidian-smart-connections?ref=next.iois.me) 」同样是一款快速调用大模型能力的插件。相比于上面提到的 Copilot，「Smart Connections」可以帮助我们快速发展笔记之间潜在的关系，它的基本逻辑是将笔记内容作为 embeddings（嵌入）存储起来，便于快速发现内容之间的语义关系，下图就是该插件对于英伟达相关内容的整理：

![img](https://oss.dailyio.info/dailyio/2024/10/0c395c4f886ead7692d570d6c93ead7a.webp)

使用该插件需要一些「门槛」，比如你需要拥有大量的笔记，只有大量的内容，才能构建起丰富的联系；再比如，其嵌入模型对于中文的支持力度比较差，如果都是中文笔记，使用起来的体验并不好。

但对我来说，由于前期收集了大量网页内容（很多都是英文内容），打开任何一条新收集的内容，使用「Smart Connections」看看有哪些相关的笔记可以参考（注意下图右侧的评分，分数越高相关度越高），也不失为一个提升效率的关键步骤：

![img](https://oss.dailyio.info/dailyio/2024/10/880b309e76bc7459531331634e425a9e.webp)

**人类与机器共同写作**

Obsidian 的编辑器并不好用，好在 Obsidian 使用通用的 Markdown 格式存储内容，这也为我们调用其他文本编辑器、编辑 Obsidian 里的内容提供了便利，我常用的是 iA Writer，可以非常便捷地打开 Obsidian 文件夹里的文件，编辑或预览均可：

![img](https://oss.dailyio.info/dailyio/2024/10/287137c02eae321f485489fa97bdfa7d.webp)

使用外部编辑器的好处有两个。其一，可以「真正」摆脱 Obsidian 难用的编辑体验，你可以选择任何一个自己喜欢的编辑工具；其二，借助 macOS 15 上自带分屏功能，你可以把 Obsidian 和写作工具（比如 iA Writer）同时放置在一个屏幕，一遍参考一遍写：

![img](https://oss.dailyio.info/dailyio/2024/10/9d11f178f1830bb53528d3768752bbef.webp)

写作完毕，所有内容也同时存储在 Obsidian，借助诸如「Copilot」或「Smart Connections」，可以快速完成校对、润色等工作，我个人最喜欢的还是标点符号校对，可使用这句提示：

> 请校对下面这段文字的标点符号，统一替换为中文标点形式，特别是引号使用「」，除此之外，不要修改任何的文字。

**一些补充**

在引入大模型后，Obsidian 的文本管理能力有了巨大提升，但也需要看到几个局限性，比如用户需要认识到大模型对于隐私的「破坏力」，如果你的笔记工具里有大量自己的隐私信息，我建议不要使用大模型，或者你可以建几个笔记库独立存放。

更进一步，Obsidian 既不是开源工具，也不支持端到端加密，我建议可以借助一些端到端加密的备份工具，至少可以为笔记工具做一层安全加护。

此前我分享过一款免费网络存储产品 Filen，这款来自德国的网盘，支持端到端加密，而且价格优惠，通过 [这个链接](https://filen.io/r/d250fb2a8a89176f10368def213130d9?ref=next.iois.me) 注册，可以获得 20GB（10 GB+10GB 邀请）的空间，用来备份 Obsidian 的笔记库足够了。

第三，熟悉我工具流的朋友可能会知道，我一直在用 Workflowy 管理自己的工作选题和生活计划，在我看来，Workflowy 也是一类「特殊的纯文本工具」，它能以极为优雅地管理纯文本内容——从小片段记录到大段图书摘录——都能灵活自如地处理。

和 Workflowy 相比，Obsidian 尽管有着这样那样的优点，但有一点让我无法忍受，那就是列表编辑体验，即便是装上了「Outline」插件之后，Obsidian 的列表编辑能力依然非常糟糕。

在这样的背景下，我继续使用 Workflowy 的列表能力，组织、编辑自己的工作和生活，但做了几点优化，一方面，使用 Obsidian 里的笔记作为内容外链；另一方面，并使用 Markdown 标准链接语法构建链接。

这样做的好处在于，我可以随时导出 Workflowy 里的记录（比如每天的日记），然后粘贴到 Obsidian 里，不会有任何格式问题。

**尾巴**

通过一系列插件、扩展以及大模型的能力，Obsidian 成为我目前内容生产过程的重要工具。相比于使用其他笔记工具，整个过程还算简单，基本都是围绕如何实现更高效的信息消费、创造等目标，而且从 Obsidian 本身到插件、扩展，几乎都是免费产品，唯一需要付费的可能就是大模型 API 了。

插播一个小广告：Dailyio 现在提供大模型 API 中转服务，感兴趣的朋友可以在 [这里](https://api.iois.me/?ref=next.iois.me) 看一下。

---

## 大模型·应用

下面是一组近期值得关注的大模型相关应用或产品。

Dailyio 对话服务 **ChatIO** 迎来发布后的首次重要更新。其一，提高限额，每小时和每天的请求次数都大幅提升（原来是 30 和 200）：

| 时间 | 请求次数限制 |
| --- | --- |
| 每小时 | 50 次 |
| 每天（24小时） | 300 次 |

单一对话的交互次数从原来的最高 8 次提高到 12 次。

其二，新增网页抓取功能「WebPilot」，该功能可帮助您直接读取网页 url 里的信息而不必输入网页正文，您可在任意模型服务里调用，如下图所示：

![img](https://oss.dailyio.info/dailyio/2024/10/cbc8343c330d8ae48796e5348cc36659.webp)

当然，「WebPilot」也不是万能的网页抓取工具，很多网站会做限制，各位需要根据实际情况，灵活使用。

Dailyio Premium 或终身会员可免费使用 ChatIO，还未申请该服务的朋友可在 [这里](https://next.iois.me/chatio-preview-beta-welcome/) 了解详情。

Google 文生图模型 [Imagen 3](https://imagen.research.google/?ref=next.iois.me) 已经免费开放，Imagen 3 的主要改进在于更高的图像真实度，具体体现在：

- 更准确的灯光效果
- 对现实世界场景和动物的更逼真还原
- 对人物的刻画更加真实

用户现在可以通过 [Gemini 网页版](https://gemini.google.com/?ref=next.iois.me) 免费使用该产品：

![img](https://oss.dailyio.info/dailyio/2024/10/bd9c4685b63abf69466c2f08fd5e4cfc.webp)

本地大模型管理工具 **LM Studio** 新版本（0.3.4）引入了基于 MLX 的新引擎，为搭载 Apple Silicon 的 Mac 用户提供更高效的本地模型运行体验。

[MLX](https://github.com/ml-explore?ref=next.iois.me) 是苹果推出的开源 AI/ML 软件栈，专为 Apple Silicon 优化，能够充分利用 Apple M 系列芯片的强大加速硬件。此次 LM Studio 的 MLX 引擎是一个开源 Python 模块，结合了 mlx-lm、Outlines 和mlx-vlm 等软件包，支持多种模型类型和结构化输出。

你可以在 [这里](https://lmstudio.ai/download?ref=next.iois.me) 下载或更新 LM Studio。

可能有一些朋友不知道 OpenRouter 上有大量免费模型，你可以通过 [这里](https://openrouter.ai/models?order=pricing-low-to-high&ref=next.iois.me) 查看更多，推荐其中几个我自己用起来不错的模型：

- [liquid/lfm-40b](https://openrouter.ai/liquid/lfm-40b?ref=next.iois.me) ：一个 403 亿参数的专家混合模型 (MoE)，速度非常快，而且不是传统的 Transformer 架构；
- [google/gemini-flash-1.5-8b-exp](https://openrouter.ai/google/gemini-flash-1.5-8b-exp?ref=next.iois.me) ：Google Gemini 系列的最新小模型，中文支持不错，而且速度非常非常快；
- [nousresearch/hermes-3-llama-3.1-405b:free](https://openrouter.ai/nousresearch/hermes-3-llama-3.1-405b:free?ref=next.iois.me) ：微调的 Llama-3.1 405B 基础模型，没太多特点，免费或许是最大的特点；
- [meta-llama/llama-3.1-405b-instruct:free](https://openrouter.ai/meta-llama/llama-3.1-405b-instruct:free?ref=next.iois.me):这是 SambaNova 公司提供的 Llama-3.1 405B 版本，速度非常非常快；

你可以 **免费注册 OpenRouter** ，然后通过 API 调用这些模型即可，完全可以满足个人自用的需求。推荐以下几个大模型 API 调用渠道：

- 网页端： [Chatbox](https://chatboxai.app/zh?ref=next.iois.me) 、 [LobeChat](https://github.com/lobehub/lobe-chat?ref=next.iois.me) 、 [Chatgpt Next Web](https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web?ref=next.iois.me) ；
- iOS： [ChatX](https://apps.apple.com/us/app/chatx-ai-%E6%99%BA%E8%83%BD%E9%97%AE%E7%AD%94-%E7%BF%BB%E8%AF%91-%E5%86%99%E4%BD%9C-%E7%BB%98%E7%94%BB-%E8%AF%AD%E9%9F%B3-%E6%A8%A1%E5%9E%8B/id6446304087?l=zh-Hans-CN&ref=next.iois.me) 、 [OpenCat](https://opencat.app/zh-Hans/?ref=next.iois.me) 、 [Pal Chat](https://apps.apple.com/us/app/pal-chat-ai-chat-client/id6447545085?l=zh-Hans-CN&ref=next.iois.me) ；
- Android： [BotGem](https://botgem.com/?ref=next.iois.me) ；

---