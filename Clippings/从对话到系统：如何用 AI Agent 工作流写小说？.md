---
title: "从对话到系统：如何用 AI Agent 工作流写小说？"
source: "https://articles.zsxq.com/id_lir0vige07qw.html"
author:
  - "[[王树义]]"
published:
created: 2026-03-02
description:
tags:
  - "clippings"
---
[来自： 玉树芝兰](https://wx.zsxq.com/group/5825428444)

讲述 22000 **字** AI 小说创作背后的工程化思维，这或许是你应用 AI 的一次范式变革。

  

![](https://article-images.zsxq.com/FtcmoERcRdGBdiY_ByZ2G4mbq22j)

  

  

## 小说

  

我最近在公众号发了一篇文章《 [（AI 小说）代码消亡史：一个 33 岁程序员的 AI 求生指南](https://mp.weixin.qq.com/s/Ggp69MoSsdbXi3BpX--K1w) 》。

  

当我把「AI 小说」这 4 个字加到题目里的时候，我就知道它至少能让阅读量降低 60%。

  

而且我还很诚实地开启了「内容由 AI 生成」的创作说明。这保证了系统推荐概率大幅降低。

  

![](https://article-images.zsxq.com/FuRfe0Qsoo1Pt4gDpZbE8HPzXuiY)

  

果不其然，很多人根本连打开的意愿都没有。这篇文章的阅读量创下近期新低。

  

但是，它依然获得了数十次转发。而且还有不少读者在后面认真留言回复。

  

![](https://article-images.zsxq.com/Fk8elRzFSWxcjV5gqccW3AzgsCn-)

  

这说明，它不是又一篇「AI 生成的垃圾内容」，而或许是你应该值得认真对待的现象 —— 当你还在一遍遍调整提示词，期待 AI 一次性生成完美内容时，AI Agent 模式正在将人机交互从简单的「问答」升级为复杂的「项目执行」系统。

  

刚好最近星球里面星友提问，我的工作流有没有新的升级？其实，这就是。

  

![](https://article-images.zsxq.com/FoXjIMGu7el5cueN1IjNOtI2LTtK)

  

本文我就以这篇小说的创作过程，带你深入理解这种新范式如何通过 50+ 个文件、15 个执行步骤、12 项质量指标，将一个简单的主题转化为两万多字的作品。更重要的是，你将学会如何设计自己的 AI Agent 系统，让 AI 不再是随机的文本生成器，而是可控、可追溯、可迭代的生产力工具。

  

## 对比

  

传统的对话式 AI 就像一个聪明但健忘的助手，你问一句，它答一句，却无法管理复杂的、多步骤的项目。当然，目前 ChatGPT 和 Claude 都在加入记忆功能，也算是对这种模式局限的补足。但是，如果你的任务专业化更强，那么这种简单加入多篇对话记忆的补丁，可能帮助有限。

  

例如，当你输入「写一个程序员面对 AI 冲击的故事」时，传统 AI 会立即生成一个 2000 字的简单故事，质量参差不齐。

  

![](https://article-images.zsxq.com/Fkf7DIVXVACQWPYfwQ_e38dFDj-w)

  

别担心，没那么长，你看，两屏截下来，就结束。

  

![](https://article-images.zsxq.com/FuIJGrr1fg5rjel_9Pn_SSURtFfQ)

  

这里我用的还是目前 OpenAI 的旗舰模型 GPT-5。

  

这样的东西，你要说读者爱读，我是不信的。

  

而 Agent 模式的处理方式完全不同。

  

这是我最近这篇小说的开头。

  

![](https://article-images.zsxq.com/Fsnu2IpI7EPrBjYWkaL--c0V1Kjx)

  

你能想象吗？小说的一开头，就直接设置了这么高的阅读门槛，居然把代码直接放在上面了。

  

![](https://article-images.zsxq.com/Fh_BiNzXlJOsYaDAkyIVCBzoh9uY)

  

第二屏，就涉及到这个代码段的问题，甚至还有解决方案。难怪有人说，你这小说，阅读起来需要专业背景。

  

其实不光是专业背景。你看这些细节。无论是编辑器名称，键盘的型号，以及 FPS 游戏磨损的键位，全都透露着一种细节的到位……

  

再看这个章节。

  

![](https://article-images.zsxq.com/Fg9ClG-kQ1Gg9iLnQK8srvMwnfsC)

  

这里的细节到什么程度？你看看下面这张高德地图的截图就明白了。

  

![](https://article-images.zsxq.com/Fvfa6avrcYjfcBsExBF8xVR3CU1B)

  

要达成这种效果，需要用户做什么？

  

很多好友都猜测：

  

你是不是反复对话，人工找出问题，让 AI 逐个修改啊？

  

你太不了解我了。有那功夫我自己写不就得了？

  

「懒人」是有底线的 —— 这么复杂的活儿，不干。

  

这个小说的结果，其实是我一站式输入提示词后，AI 直出稿件。

  

当然，为了保证结果的质量，我又让另一个 AI 对这个结果做了「同行评议」，然后自动修改出来的。因为实话实说，虽然我这几年也往北京跑过不少趟。但你不让我开高德直接问国贸到团结湖坐地铁几号线？几站地？

  

我根本答不上来的。

  

都是一站式输入提示词，为什么效果差那么远呢？

  

因为，在我输入提示词后，AI 首先创建了 15 个目录，制定了详细的执行计划，进行了 30 条事实调研，设计了 12 条伏笔线，经过三轮改稿，最终产出了 22000 字的专业作品。

  

这种差异的背后，是两种完全不同的思维范式。传统对话模式是「线性思维」—— 问题直接导向答案；而今天咱们展示的 Agent 模式是「系统思维」—— 将任务分解、规划、执行、验证、迭代，形成一个完整的工作流程。

  

Agent 模式的革命性在于，它将 AI 从一个「回答问题的工具」转变为一个「执行项目的系统」。这就像从「向朋友征求建议」升级到「花钱聘请专业团队完成项目」。通过提供结构化的流程（提示词）和持久化的记忆（文件系统），Agent 才突破了 AI 的上下文限制，获得了处理复杂任务的能力。

  

让我们通过一个具体的对比表来理解这两种模式的差异：

  

![](https://article-images.zsxq.com/FmbsSVc3kHiFjVJC02P20EtXwh_D)

  

具体到技术实现上，Agent 模式通过四个核心组件实现了这种转变。

  

第一是「用户」，你只需要提供最高层的目标，比如我给定的目标为「2025 年，AI 冲击下，一个 33 岁程序员」。你没看错，我根本就没有提供更多的背景信息，更不可能给出剧情走向。

  

第二是「提示词」，这不是简单的提出要求和问题，而是包含角色定义、执行步骤、质量标准的完整「标准作业流程」。

  

![](https://article-images.zsxq.com/FoqkL2q7FL0lN1HGjtjNFH6HMW7M)

  

第三是「AI 执行者」，它严格按照流程执行，不需要额外指导。

  

第四是「文件系统」，作为 AI 的外部记忆和工作空间，突破了 AI 大模型上下文窗口的限制。尽管目前已经有大模型把上下文长度整到了 2M tokens，但是比起你的磁盘容量，还是小巫见大巫了。

  

这种架构带来的改变是根本性的。你不再需要反复调试提示词，期待 AI 「猜中」你的意图。相反，你可以像管理软件项目一样管理 AI 任务 —— 有需求分析、系统设计、迭代开发、测试验证、最终交付。每个环节都是可控的、可追溯的、可优化的。

  

更重要的是，这种模式是可复用和可扩展的。一旦你设计好一个 Agent 流程，它就可以稳定地执行同类任务，质量有保障，结果可预期。

  

例如用同样的提示词，我换了个主题「2025 年，AI 冲击下，一个中国二本院校教信息检索的大学讲师，37 岁」。

  

于是，这样一篇文章就哗啦啦生成出来了。

  

![](https://article-images.zsxq.com/FhoGNXEn3r1FnfOtm_Kklk5NmacQ)

  

我发给了几个有切身体验的大学教师朋友们试读，他们都很感兴趣。

  

![](https://article-images.zsxq.com/FpE00U65jLV9GSmbbwY_bf-tfu7Z)

  

  

## 架构

  

讲清楚基本的原理，咱们来深入 Agent 系统的内部。你会发现它模拟了一个完整的创作团队。

  

注意这不是简单的拟人化，而是通过角色分工实现了复杂任务的模块化管理。让我们看看这个「虚拟团队」是如何协同工作的。

  

在小说创作 Agent 中，系统设计了五个核心角色，每个角色都有明确的职责和产出。「小说作者」负责实际的文本创作，从 25000 字的初稿到 22000 字的精炼版本。「设定师」构建故事世界，创建了包含 30 条事实卡片的世界观设定。「情节设计师」负责故事结构，设计了四章架构和 12 条伏笔线。「连续性校对」确保时间线、人物关系的一致性。「敏感度读者」审查内容的社会影响，避免刻板印象。

  

这种角色设计的精妙之处在于，每个角色都对应着特定的文件输出。设定师产出 bible/world.md，情节设计师产出 beats/structure.md，连续性校对维护 continuity/checks.md。这些文件不是临时的中间结果，而是持久化的项目资产，可以被其他角色读取和引用。

  

![](https://article-images.zsxq.com/Fkjjc1wfSNciN5ND8gMc8FPLd6iK)

  

文件系统在这里扮演了「外部认知架构」的角色。传统 AI 的致命弱点是上下文窗口限制 —— 通常只能处理几千到几万字的信息。而 Agent 通过文件系统突破了这个限制。每个目录对应大脑的不同功能区：bible/ 是长期记忆（规则和世界观），facts/ 是知识记忆（调研和验证），continuity/ 是逻辑记忆（伏笔和关系追踪），draft/ 是工作记忆（迭代过程）。

  

让我们看一个具体的协同案例：处理「AI 生成代码 bug」这个关键场景。首先，设定师在 facts/ 目录下调研了 Redis 分布式锁的技术细节。然后，情节设计师将其设定为第一章的核心冲突。

  

![](https://article-images.zsxq.com/Fv3CTSHBrgy6a6P-ZOjZlOtW8_YI)

  

接着，作者撰写了包含准确代码的技术场景。随后，连续性校对验证了代码的技术准确性。最后，敏感度读者确保描写不会贬低年轻程序员。这个过程生成了多个相互关联的文件，形成了完整的证据链。

  

这种协同机制的优势是显而易见的。首先是专业性 —— 每个角色专注于自己的领域，避免了「全能型 AI」的平庸。其次是可追溯性 —— 每个决策都有文件记录，可以回溯和审计。最后是可扩展性 —— 你可以根据需要增加新角色，比如「技术顾问」或「市场分析师」，整个系统依然能够顺畅运行。

  

## 步骤

  

为什么需要 15 个步骤来完成一个创作任务？

  

答案是：复杂任务需要系统化的方法。就像建造房屋需要从地基到装修的完整流程，高质量的内容创作也需要从调研到验证的全过程管理。

  

整个流程可以分为四个阶段，每个阶段都有明确的目标和产出。

  

**基础构建阶段（Step 00-03）** 就像项目的「打地基」。Step 00 创建了项目骨架，包括 15 个目录和核心规划文件 plan.md。

  

![](https://article-images.zsxq.com/Fuj8ctec-etiYuMcXUpVgNu5wBCa)

  

Step 01 澄清主题，不是简单理解字面意思，而是深度解析 —— 将「程序员面对 AI 冲击」解读为「在被替代的恐慌中重新定义人的价值」。

  

![](https://article-images.zsxq.com/FmsKl70ylhVhPJLFloi9DNKAvwoM)

  

Step 02 锁定技术规格，确定了第三人称视角、过去时态、冷峻写实的基调。

  

![](https://article-images.zsxq.com/FtdHRwCq5b2nYa20iqZUx5247hcK)

  

Step 03 进行现实调研，收集了 30 条事实卡片，从 AI 工具定价到程序员薪资，每个细节都有据可查。

  

![](https://article-images.zsxq.com/FtzFN50YY3k1cjfhGdUERUNHqLpF)

  

**设计规划阶段（Step 04-07）** 是「画图纸」的过程。

  

Step 04 创建人物卡，不是简单的姓名年龄，而是包含核心恐惧、转变弧线、标志性台词的立体角色。

  

![](https://article-images.zsxq.com/Flv_w0cEZNBi4JXX99AkZE7VvGVU)

  

这里是人物关系：

  

![](https://article-images.zsxq.com/FjUJ2G76shtYGrcZmP8QegKKwzFx)

  

Step 05 设计情节结构，规划了四章的关键拍点：开端事件、催化剂、中点反转、黑暗时刻、最终转变。

  

![](https://article-images.zsxq.com/FjWixSPIIk_9WSZ6XVDvyh47JurL)

  

Step 06 设计场景卡，每个场景都用「目标 - 冲突 - 结果」模式设计。

  

![](https://article-images.zsxq.com/FrcyYL0nOQ3BG8vU6fCFsppH55Fg)

  

AI 还提供了具体的事件列表。

  

![](https://article-images.zsxq.com/Fhp9AhScRhDLNNbLhj3xP-cfjr0M)

  

Step 07 确定文风，提供了具体的样例段落作为「风格单元测试」。

  

![](https://article-images.zsxq.com/FqbQNAFiZm9noUhpaj9CU3V_RdeT)

  

实话实说，这一阶段里不少黑话，我自己是根本不懂的。但是它们作为内容创作行业的经验和惯例，AI 掌握起来得心应手。

  

**写作执行阶段（Step 08-10）** 采用了独特的「三遍改稿」策略。Step 08 是「写满」——不设限制地输出所有素材，生成了 25000 字的初稿。

  

![](https://article-images.zsxq.com/Fn81V7Tn1O2Z22Sd-apOK9_c6E8r)

  

Step 09 进行连续性检查，发现并修正了 15 处逻辑错误，比如时间线跳跃、数据不一致。Step 10 是「萃取」—— 删除冗余，强化关键信息，将初稿精炼到 22000 字。

  

**打磨验证阶段（Step 11-15）** 确保质量达标。Step 11 进行敏感度审查，将「35 岁程序员都会被淘汰」改为「35 岁被视为分水岭」。Step 12 强化主题回环，确保「人机协作」的核心理念贯穿全文。Step 13 进行技术核对，验证每个技术细节，从 Redis 命令语法到地铁末班时间。Step 14 评估饱和度，检查 12 项质量指标是否全部通过。Step 15 输出最终成果。

  

这个流程的精妙之处在于其工程化思维。每个步骤都有明确的输入、处理、输出，都生成可验证的中间产物。这不是线性执行，而是允许迭代和回环 —— 如果 Step 09 发现问题，可以回到 Step 06 修改场景设计。模型可能会健忘，或者飘出去，但是这些落盘的文件是真实存在的，所以只要模型认真参考，总能把思绪拉回来。

  

不仅如此，通过这种方式，Agent 将创作过程从「黑箱」变成了「白箱」，你可以清楚地看到每一步的决策和产出，可以在任何环节介入和调整。如果你自信故事讲述能力足够强，可以中间叫停，手动修改后，让 AI 从某一步骤继续执行即可。

  

## 实战

  

理论很重要，但你更需要看到 Agent 在实际工作中是如何处理具体问题的。我们通过三个真实案例，深入了解 Agent 如何将复杂问题分解、处理、整合，最终产出专业级的内容。

  

**案例一：技术细节的多层处理** 。场景需求是描写主角发现 AI 生成代码的致命 bug。传统 AI 可能只会写「李晓明发现了一个严重的 bug」。而 Agent 的处理展现了惊人的深度。首先在 Step 03，系统调研了 Redis 分布式锁的正确实现、并发控制的常见陷阱、GitHub Copilot 的已知局限，然后在 Step 06，将这个技术冲突设计为展现「AI 不理解分布式系统上下文」的关键场景。Step 08 的初稿包含了完整的错误代码和修正代码，精确到每一行的注释。Step 13 的技术核对验证了 Redis 命令语法、分布式问题的真实性、修复方案的可行性。最终呈现的不是简单的「发现 bug」，而是包含准确代码、深层技术思考、人物情感反应的立体场景。

  

**案例二：人物情感的递进刻画** 。需求是展现主角从抗拒到接受 AI 的心理转变。Agent 设计了四层递进的情感弧线。第一层（第 1 章）是外在抗拒——「李晓明删掉整个代码块，机械键盘发出清脆的哒哒声，像某种古老的仪式」。第二层（第 2 章）是被迫尝试——「时间过去五分钟了，李晓明才开始与 Cursor 对话，但他的方式不同」。第三层（第 3 章）是痛苦觉醒——「凌晨 4 点，他打开 ChatGPT，第一次感觉到某种可能性」。第四层（第 4 章）是主动进化——「不是 AI replacing developers，而是 AI empowering developers」。每一层都有具体的场景支撑，都有细腻的心理描写，形成了完整的转变轨迹。

  

**案例三：伏笔系统的精密设计** 。Agent 设计了 12 条伏笔线，涵盖技能、物品、对话、环境等多个维度。以「技能类伏笔 T001」为例：第 1 章设置主角深夜修复并发死锁 bug，第 2 章铺垫他在培训时展示防护栏概念，第 3 章激活刘洋的并发代码崩溃需要他救场，第 4 章回收为并发处理成为他的独特价值。每条伏笔都记录在 continuity/threads.json 中，包含设置位置、铺垫过程、激活时机、最终回收。这种精密设计确保了故事的连贯性和深度。

  

![](https://article-images.zsxq.com/FhfqCqlRw-UzJk58Qj6sstfCTope)

  

这些案例展示了 Agent 处理复杂问题的核心能力：分层处理、证据支撑、系统整合。它不是简单地生成文本，而是构建一个完整的信息网络，每个节点都有依据，每条连接都有逻辑。这就是为什么 Agent 能够产出专业级内容的原因 —— 它模拟了人类专家团队的思考和工作方式。

  

你可能会问，这样的处理是否过于复杂？答案取决于你的目标。如果你只需要一个简单的答案，传统对话模式就够了，完全没有必要「大炮轰蚊子」。但如果你需要专业级的输出、需要质量保证、需要可追溯可迭代，那么 Agent 的复杂性就是必要的投资。

  

## 质量

  

如果 AI 生成的所有内容都需要人来把控，那么对这篇小说，我会直接选择放弃 —— 我不大懂前端代码，也根本就不知道两个北京的地点之间坐几号线几站地。

  

那如何确保 AI 生成的内容达到专业标准？Agent 模式通过工程化的质量控制体系，实现自动化、标准化、可量化的质量保证。

  

Agent 的质量控制采用了「三层防护」机制。第一层是预防性控制，在开始写作之前就设定规则。bible/rules.md 文件锁定了 POV（第三人称有限）、时态（过去时）、基调（冷峻写实）、禁用词清单（奋斗、梦想、拼搏等鸡汤词汇）。这些规则像是给 AI 戴上了「约束眼镜」，从源头上避免风格偏离。

  

![](https://article-images.zsxq.com/FpxSRJbL4kX568ywrPZPvko6Cmcb)

  

第二层是过程性控制，在创作过程中实时检查。Step 09 的连续性检查会验证时间线是否一致、伏笔是否设置、人物逻辑是否合理。系统发现并修正了 15 处连续性错误，比如第 1 章是 1 月 20 日，第 2 章却跳到 3 月 15 日，中间缺少了 2 月的过渡。这种实时检查避免了错误的累积。

  

第三层是验证性控制，在完成后进行全面核查。Step 13 的技术核对要验证每个事实的准确性、每段代码的语法、每个数据的一致性。系统记录了数十个核查点：程序员薪资水平、主流 AI 工具覆盖程度、北京房租价格、通勤情况等等。30 条事实全部通过双源验证。

  

![](https://article-images.zsxq.com/Fik-z8S2yLWdRD9et_nFguxqMpiQ)

  

质量体系的核心是 12 项量化指标，存储在 out/checklist.json 中。

  

![](https://article-images.zsxq.com/Fpb-GIbkyjDKtPKlWHYhqpbkoeTc)

  

每个指标都有三个要素：测量方法、阈值标准、实际数值。比如「故事完整性」指标，测量「章节数量和段落数量」，要求「3-6 章，每章≥5 段」，实际达到「4 章，平均 8 段」。「对话比例」指标，测量「对话字数/总字数」，要求「25%-35%」，实际为「28%」。所有指标必须全部通过（PASS），任何一项失败（FAIL）都要回环修复。

  

让我们看一个质量问题的实际处理案例。系统发现初稿的对话比例达到 40%，超出了 35% 的上限。通过分析找出三个原因：初稿阶段过度依赖对话推进情节、缺少动作和环境描写、内心独白被转化为对话。解决方案包括：删除 500 字无效对话、将部分对话转化为动作描写、增加环境渲染。最终成功将对话比例控制在 28%。

  

这种质量控制体系的优势是显而易见的。首先是客观性 —— 所有标准都是可测量的，避免了主观判断的偏差。其次是自动化 —— 大部分检查可以自动执行，大大提高了效率。最后是可追溯性 —— 每个质量问题都有记录，可以分析原因和改进方法。

  

## 资源

  

看到这里，估计你也已经跃跃欲试了吧？

  

别着急，因为提示词很长，所以我 [把它放在了这个 Notion 文件里，分享给你](https://wise-pullover-00f.notion.site/AI-agent-266b21c52dac803aafd8d1bae00db952?source=copy_link) 。

  

![](https://article-images.zsxq.com/FoaDZvm6_pD-LTB8i8YX6fhNVQrd)

  

至于使用的 AI agent，我目前用的是 Claude Code，模型为 Claude 4.1 Opus。

  

你只需要用 Cursor 或者 Visual Studio Code 打开一个新文件夹，进入 Claude Code 模式，把提示词 + 你想要写作的主题输入，然后就可以看着 AI 自己欢快干活儿了。

  

当然，目前同类产品已有多种，所以你都可以尝试一番。只不过 Codex CLI 目前效果欠佳 —— 生成的小说寥寥数语，很煞风景。

  

![](https://article-images.zsxq.com/Fh3bxwQlTzUOyLlK8Oc3ygYsAF1h)

  

你看，一个截屏居然已经囊括了两章半的内容。

  

如果你能找到 Codex CLI「过度言简意赅」的破解之法，也欢迎分享到留言区，咱们一起提升。

  

## 结语

  

通过这篇深度解析，你已经了解了 AI Agent 工作流模式的原理、技术创新和实践方法。这不仅仅是一种新的技术工具，更是一种全新的思维范式 —— 将 AI 从简单的问答工具升级为复杂的项目执行系统。

  

Agent 模式工作流的核心价值在于：它让 AI 变得可控、可追溯、可迭代，同时保留了 AI 的自适应和灵活性。通过文件系统突破记忆限制，通过角色分工实现专业化，通过质量指标保证输出标准，通过迭代优化持续改进。这些创新共同构成了一个完整的生产系统。

  

更重要的是，这种模式是可学习、可复制的。你不需要成为 AI 专家，只需要掌握系统设计的原则和方法，就能创建自己的 Agent 系统。从简单任务开始，逐步积累经验，最终你会发现自己已经从「AI 使用者」进化为「AI 系统设计者」。

  

未来已来，只是分布不均。那些率先掌握更好的人机协同方式的人和组织，将在 AI 时代获得巨大的竞争优势。所以，你不妨从今天就开始动手尝试，先从写一篇有趣的小说开始。

  

祝 AI agent 工作流辅助的内容创作愉快！

  

如果你觉得这篇文章对你有帮助,欢迎分享。如果有读者从你的分享路径订阅,你可以按照规则 **获得分成奖励** 。

  

## 延伸阅读

  

1. [AI 工作流长文写作能力重大改进，欢迎你来试试看](https://articles.zsxq.com/id_6um9h6c5jrdo.html)
2. [AI 应用蓬勃爆发，你的「护城河」足够宽吗？](https://mp.weixin.qq.com/s/-H-Q70wBTDaN7APYnRhI6g)
3. [AI 时代的真稀缺技能：从「有技术」到「会洞察」](https://mp.weixin.qq.com/s/xEAWepdqRlq2kG6-rEtzbQ)
4. [从枯燥理论到生动实践：AI 智能代理如何用交互式教程讲解复杂概念](https://mp.weixin.qq.com/s/9o2xEsAClOnrn2GhuBryBA)
5. [本地 AI + 自动捕获：打造属于你自己的知识管理系统](https://mp.weixin.qq.com/s/qJpfnF8JjqrolrvP9UleVg)

  

![](https://articles.zsxq.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)

扫码加入星球

查看更多优质内容

https://wx.zsxq.com/mweb/views/joingroup/join\_group.html?group\_id=5825428444