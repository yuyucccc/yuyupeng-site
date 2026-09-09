# yuyupeng.com

Static portfolio site. No framework, no build tooling — the `.html` files in this
repo are what gets served.

---

## Putting it online (first time)

You need a GitHub account. Replace `USERNAME` below with your GitHub username.

### 1. Make an empty repository on GitHub

Go to <https://github.com/new>. Name it `yuyupeng-site`. **Do not** tick
"Add a README", "Add .gitignore" or "Choose a license" — the repo must be empty,
otherwise the next step conflicts.

### 2. Push this folder to it

```bash
cd /Users/uu/Archive_Portfolio/website/yuyupeng-site
git remote add origin https://github.com/USERNAME/yuyupeng-site.git
git push -u origin main
```

GitHub will ask for a password. **Your account password will not work** — you need
a Personal Access Token instead: <https://github.com/settings/tokens> → "Generate
new token (classic)" → tick `repo` → copy the token and paste it as the password.
macOS will remember it after the first time.

### 3. Turn on GitHub Pages

In the repo: **Settings → Pages**. Under "Build and deployment", set Source to
**Deploy from a branch**, branch **main**, folder **/ (root)**. Save.

Wait a minute, then your site is live at `https://USERNAME.github.io/yuyupeng-site/`.

### 4. Point yuyupeng.com at it

**Buy the domain first** (~€10–15/year). Any registrar works — TransIP and
Namecheap are both fine.

At the registrar, open the DNS settings and add these records:

| Type | Name | Value |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| AAAA | `@` | `2606:50c0:8000::153` |
| AAAA | `@` | `2606:50c0:8001::153` |
| AAAA | `@` | `2606:50c0:8002::153` |
| AAAA | `@` | `2606:50c0:8003::153` |
| CNAME | `www` | `USERNAME.github.io` |

Then back in **Settings → Pages → Custom domain**, type `yuyupeng.com` and save.
Once the check passes, tick **Enforce HTTPS**.

DNS can take anywhere from ten minutes to a few hours to take effect. The
`CNAME` file in this repo already contains `yuyupeng.com`, so don't delete it.

---


## 在本机看网站

**双击 `打开网站.command`** —— 浏览器会自动打开，关掉弹出的终端窗口就停止。

第一次双击如果 macOS 提示「无法打开，因为它来自身份不明的开发者」：
在文件上点右键 → 打开 → 再点「打开」。之后就可以直接双击了。

首页中间的 logo 动画是 `assets/js/personal-logo-fusion.js`（你自己做的组件）。
参数写在 `templates/home.html` 的 `<personal-logo-fusion>` 标签上：
`duration` 每圈秒数、`minimum` 收缩到的比例、`fill-strength` 不透明度。
改完跑 `python3 build.py`。

## Changing the site later

**All text lives in `content.json`.** Never edit the `.html` files — they are
generated and your changes would be overwritten.

1. Edit `content.json`
2. Regenerate:
   ```bash
   cd /Users/uu/Archive_Portfolio/website/yuyupeng-site
   python3 build.py
   ```
3. Preview locally at <http://localhost:8899>:
   ```bash
   python3 -m http.server 8899
   ```
4. Publish:
   ```bash
   git add -A
   git commit -m "Update Kameleon description"
   git push
   ```

The live site updates about a minute after the push.

首页左边的三行筛选（all / professional works / academic works）按 `content.json`
里每个项目的 `group` 字段分组。要从首页拿掉一个项目，改 `build.py` 里
`GALLERY` 那行的排除名单——被排除的项目连同它的项目页一起不再生成。

### Adding a project

Add an object to the `projects` array in `content.json`, then put its images in
`assets/img/<slug>/` named `01.jpg`, `02.jpg`, … and add matching entries to
`assets/img/manifest.json` (each needs `file`, `w`, `h`). Run `build.py`.

### Changing a project's cover image

Add `"hero": "03.jpg"` to that project in `content.json`. Without it the first
image is used.

---

## What is what

| File | |
|---|---|
| `content.json` | **all the text** — the only file you normally edit |
| `build.py` | generates the HTML |
| `assets/img/manifest.json` | image list with dimensions |
| `assets/css/v2.css` | all styling |
| `assets/js/personal-logo-fusion.js` | the logo animation, her own component |
| `assets/fonts/` | Instrument Sans, self-hosted (SIL Open Font License) |
| `PRODUCT.md` / `DESIGN.md` | why the site is built the way it is |
| `CNAME` | the custom domain — required by GitHub Pages |
| `.nojekyll` | stops GitHub from reprocessing the files |

## Still to do

Three academic project descriptions are drafts written from the drawings, not
from your own text. They are marked with `draft_note` in `content.json` and the
note is printed on the page — read them and either rewrite or delete the note:

- `tidal-park`
- `beautiful-decay`
- `circular-community`
