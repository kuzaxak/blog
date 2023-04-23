---
title: "Hello World!"
description: |
    First blog post here. Hugo initial setup and simple hosting
    on Digital Ocean static apps.
tags: []
date: 2023-04-23
slug: "hello-world"
tldr: |
    Nothing fancy. Digital Ocean App hosting + basic theming.
---

I decided to start writing posts and was curious about what type of blog to start.
As an engineer, I wanted the flexibility of Markdown, version control traceability,
and automatic rollouts.

I chose Hugo for static website generation and, for now, Digital Ocean apps for serving pages.
Later on, I'll migrate to AWS CloudFront.

### Theming

Initially, I considered an interactive [shell-like][1] theme, but it would be too nerdy.
So, I opted for [Archie][2] as the main theme, which provided a minimalistic, engineering-like blog style.

If you cloned your theme to a sub-path with `git clone`, don't forget to create a `.gitmodules` file;
otherwise, the DO builder won't pull the theme from the target repository.

```
[submodule "themes/archie"]
  path = themes/archie
  url = https://github.com/athul/archie.git
```

### Deploy

DO apps offer an easy deployment process. A simple YAML file placed in `.do/app.yaml`
provides everything needed to deploy a static app:

```yaml 
name: static-hugo
static_sites:
- build_command: rm -r ./public; hugo --destination ./public
  environment_slug: hugo
  github:
    branch: master
    deploy_on_push: true
    repo: kuzaxak/blog
  name: static-hugo
```

I bound the DNS to DO nameservers on the Namecheap main page. Remember to check that they're
propagated, and you can continue with:

```bash
dig NS kuzaxak.dev
```

After creating a DO App, follow the wizard – it's self-explanatory. You'll get a DO subdomain.
Attach your domain on the Settings page, and you'll automatically receive `A` records
in your DNS zone.

### Fine tuning

DO apps require default pages to be present in the final filesystem folder:
* `index.html`
* `404.html`

Hugo creates `index.html` without any additional configuration. 

`404.html` might be created by the theme, but not in my case. The theme's `404` was empty.
Easily fix this by creating a `layouts/404.html` [file][3]. Copy your theme's `index.html`
and add a helpful error message to guide people back or report a broken link.

Check that DO detects your content in the build log. It should look like this:

```
› static site output directory is not explicitly set, attempting to look for static files
[2023-04-23 11:47:52] │      checking /workspace/_static: not found
[2023-04-23 11:47:52] │      checking /workspace/dist: not found
[2023-04-23 11:47:52] │      checking /workspace/public: found
[2023-04-23 11:47:52] │  ✔ using document root /workspace/public
[2023-04-23 11:47:52] │ 
[2023-04-23 11:47:52] │ => Uploading files to Spaces
[2023-04-23 11:47:52] │     categories/index.html
[2023-04-23 11:47:52] │     contact/index.html
[2023-04-23 11:47:52] │     about/index.html
[2023-04-23 11:47:52] │     404.html
[2023-04-23 11:47:52] │     categories/feed.xml
[2023-04-23 11:47:52] │     feed.xml
[2023-04-23 11:47:52] │     index.html
[2023-04-23 11:47:52] │     js/feather.min.js
[2023-04-23 11:47:52] │     js/main.js
[2023-04-23 11:47:52] │     js/themetoggle.js
[2023-04-23 11:47:52] │     page/1/index.html
[2023-04-23 11:47:52] │     robots.txt
[2023-04-23 11:47:52] │     sitemap.xml
[2023-04-23 11:47:52] │     tags/feed.xml
[2023-04-23 11:47:52] │     tags/index.html
[2023-04-23 11:47:52] │ 
[2023-04-23 11:47:52] │ => Configuring index document: index.html
[2023-04-23 11:47:52] │ => Configuring error document: 404.html
[2023-04-23 11:47:52] │ => Uploaded 34 files
```

### Content

Adding content is pretty easy. I recommend using date prefixes for the posts.
This way, you can easily get a sorted list without introducing subfolders.

To automate date parsing from a new file name, create `archetypes/posts.md` with a parser regex:

```yaml
---
title: "{{ replace (.Name | replaceRE "^[0-9]{4}-[0-9]{2}-[0-9]{2}-" "") "-" " " | title }}"
description: |
  Description
tags: []
date: {{ .Name | replaceRE "^([0-9]{4}-[0-9]{2}-[0-9]{2}).*" "$1" }}
slug: "{{ .Name | replaceRE "^[0-9]{4}-[0-9]{2}-[0-9]{2}-" "" }}"
---

```

Now, you'll be able to create your first page. I started with this article to practice
writing.

```bash
hugo new posts/2023-04-23-hello-world.md
```

### Stats

You're probably curious if anyone is actually reading your blog. To find out, you can add Google Analytics,
which is supported by Hugo.

Register your website and prove ownership via DNS; after that, you'll receive a G-tag code.

Add it to your `config.toml`; mine looks like this:

```toml
relativeURLs = true
baseURL = "/"
languageCode = "en-us"
title = "Vladimir Kuznichenkov | Engineer"
author = "Vladimir Kuznichenkov"
theme = "archie"
copyright = "© Vladimir Kuznichenkov"

# get information about the Git repo, such as last commit to a file
enableGitInfo = true

# Code Highlight
pygmentsstyle = "monokai"
pygmentscodefences = true
pygmentscodefencesguesssyntax = true

paginate=5

googleAnalytics = 'G-MEASUREMENT_ID'
enableRobotsTXT = true

[params]
  mode = "toggle"
  author = "Vladimir Kuznichenkov"
  copyright = "@ Vladimir Kuznichenkov"
  WebMentionDomain = "kuzaxak.dev"
  mathjax = true # enable MathJax support
  katex = true # enable KaTeX support

# Social Tags
[[params.social]]
  name = "GitHub"
  icon = "github"
  url = "https://github.com/kuzaxak/blog"

[[params.social]]
  name = "Twitter"
  icon = "twitter"
  url = "https://twitter.com/kuzaxak/"

[permalinks]
  posts = "/posts/:year/:month/:day/:slug/"
  tags = "/tags/:title/"

[outputFormats]
[outputFormats.rss]
  mediatype = "application/rss"
  baseName = "feed"

[markup]
  [markup.goldmark]
    [markup.goldmark.extensions]
    typographer = false
    [markup.goldmark.renderer]
    # allow inline HTML, such as spoiler warnings
    unsafe = true
  [markup.tableOfContents]
  startLevel = 1
  endLevel = 6
  ordered = false

[menu]
  [[menu.main]]
    identifier = "blog"
    name = "./blog"
    url = "/posts"
    weight = 2
  [[menu.main]]
    identifier = "about"
    name = "./about"
    url = "/about"
    weight = 3

  [[menu.footer]]
    name = "Tags"
    url = "/tags"
    weight = 4

[sitemap]
  changefreq = 'monthly'
  filename = 'sitemap.xml'
  priority = 0.5
```


[1]: https://themes.gohugo.io/themes/hugo-theme-shell/
[2]: https://themes.gohugo.io/themes/archie/
[3]: https://gohugo.io/templates/404/