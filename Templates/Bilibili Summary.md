---
type: bilibili-summary
title: {{title}}
uploader: {{uploader}}
url: {{url}}
bvid: {{bvid}}
duration: {{duration}}
date_published: {{date_published}}
date_summarized: {{date_summarized}}
views: {{views}}
likes: {{likes}}
coins: {{coins}}
favorites: {{favorites}}
danmaku: {{danmaku}}
shares: {{shares}}
replies: {{replies}}
tid: {{tid}}
tname: {{tname}}
typename: {{typename}}
tags:
  - source/bilibili
  - video
{{#each tags}}
  - {{this}}
{{/each}}
---

# {{title}}

> [!info] 📺 [{{uploader}}](https://space.bilibili.com/{{uploader_mid}}) | {{duration}} | {{views}} views
>
> **Stats**: 👍 {{likes}} | 🪙 {{coins}} | ⭐ {{favorites}} | 💬 {{danmaku}} danmaku

## AI Summary

{{summary}}

---

## Key Metadata

- **Video URL**: {{url}}
- **Upload Date**: {{date_published}}
- **Video Type**: {{typename}}
- **Partition**: {{tname}}
- **BV ID**: {{bvid}}
- **Duration**: {{duration}}

## Tags

{{#each tags}}
- {{this}}
{{/each}}

{{#if description}}

## Video Description

{{description}}

{{/if}}

{{#if subtitles}}

---

## Subtitles

> [!abstract]- Full Subtitle Transcript
{{#each subtitles.split('\n')}}
> {{this}}
{{/each}}

{{/if}}
