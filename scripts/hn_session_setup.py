#!/usr/bin/env python3
"""
One-time HN session setup: open a fresh Chromium session with a persistent profile
so the user can complete manual login+cookies for HN automation reuse.
"""
from __future__ import annotations
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path('/home/oengakeenlay/browser-agent')
PROFILE = BASE / '.playwright-hn-profile'
PROFILE.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(str(PROFILE), headless=False, user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ))
        page = context.new_page()
        page.goto("https://news.ycombinator.com/login", wait_until="domcontentloaded")
        print('OPENED_HN_LOGIN_URL=', page.url)
        print('PROFILE_PATH=', PROFILE)
        print('ACTION: complete login in the opened browser window, then submit once')
        print('After confirming /submit works, close the browser to save session')
        try:
            input('Press ENTER after manual login...')
        except EOFError:
            pass
        context.close()


if __name__ == "__main__":
    main()
