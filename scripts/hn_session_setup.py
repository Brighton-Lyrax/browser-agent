#!/usr/bin/env python3
"""
One-time HN session setup.
Launches a visible Playwright browser with a persistent profile at
/home/oengakeenlay/browser-agent/.playwright-hn-profile
so cookies/state survive between runs.
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
        context = p.chromium.launch_persistent_context(str(PROFILE), headless=True)
        page = context.new_page()
        page.goto("https://news.ycombinator.com", wait_until="domcontentloaded")
        print('OPENED_HN_URL=', page.url)
        print('OPENED_HN_TITLE=', page.title())
        if page.is_visible("text=submit", timeout=2000):
            print('SESSION_ACTIVE')
        else:
            print('MANUAL_LOGIN_REQUIRED')
        print('PROFILE_PATH=', PROFILE)
        try:
            input('Press ENTER to close...')
        except EOFError:
            pass
        context.close()


if __name__ == "__main__":
    main()
