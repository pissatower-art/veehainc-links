# @veehainc link-in-bio (Arto / ApLiQ)
Static site: index.html + images/ (data inline, also in products.json). No prices.

## Daily update
1. Ask Grok Bot to refresh `products.json` from the Amazon catalogue (needs the Amazon MCP) and download new images into `images/`.
2. Append the day's post to /workspace/instagram_posted.csv (asin,product,date_posted,permalink).
3. `python3 build.py`  → rewrites index.html ("New this week" = posted in last 7 days; `--days N` to change).
   `python3 build.py --inline` → also writes dist/index.html (single file, images inlined, ~1.7 MB).
4. `./deploy.sh` → pushes to GitHub Pages (needs `gh auth login` once).
