from lcars.base.type import Matrix, VBoxLayout, HBoxLayout, Directive, Chassis, Visual
from lcars.base.default import TitanPalette, FontStyle
from lcars.base.components import LCARSButton, style_lcars_scroll_area
from lcars.base.interface import LCARSInput
from lcars.system.board_computer import Computer as get_computer

try:
    _webview_cls = Directive.WebView
    _WEB_AVAILABLE = (_webview_cls is not None)
except Exception:
    _WEB_AVAILABLE = False

if _WEB_AVAILABLE:
    class InterceptingWebEnginePage(Directive.WebPage):
        def createWindow(self, windowType):
            return self

class AISearchThread(Directive.Thread):
    result_ready = Directive.Signal(str)
    
    def __init__(self, computer, prompt):
        super().__init__()
        self.computer = computer
        self.prompt = prompt
        
    def run(self):
        try:
            # Bypass process_query and hit the conversational AI directly
            print(f"[DEBUG] Started AISearchThread.run()")
            res = ""
            if hasattr(self.computer, 'ai') and self.computer.ai:
                print(f"[DEBUG] Using self.computer.ai.ask()")
                # Use a specific high-temperature or focused context query if supported
                res = self.computer.ai.ask(self.prompt)
            elif hasattr(self.computer, 'copilot') and self.computer.copilot._client:
                print(f"[DEBUG] Using self.computer.copilot.run()")
                res = self.computer.copilot.run(self.prompt)
            else:
                print(f"[DEBUG] No AI backend found!")
                
            print(f"[DEBUG] AI Search raw response: {res}")
            self.result_ready.emit(res)
        except Exception as e:
            print(f"[DEBUG] AISearchThread Exception: {e}")
            self.result_ready.emit("")

class StreamPanel(Matrix):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.computer = get_computer()
        self._build_ui()

    def _build_ui(self):
        c_prim = TitanPalette.Buttons[0]
        c_sec  = TitanPalette.Buttons[2]
        c_tert = TitanPalette.YellowAlert[0]

        lay = VBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # Search Bar
        search_lay = HBoxLayout()
        search_lay.setSpacing(10)

        self.search_input = LCARSInput(c_sec)
        self.search_input.setPlaceholderText("ENTER URL, STREAM ID, OR SEARCH QUERY")
        self.search_input.returnPressed.connect(lambda: self._do_search("WEB"))
        search_lay.addWidget(self.search_input, 1)

        self.btn_search_ai = LCARSButton("AI SEARCH", c_prim, shape="pill")
        self.btn_search_ai.setMinimumSize(120, 30)
        self.btn_search_ai.clicked.connect(lambda checked=False: self._do_search("AI"))
        search_lay.addWidget(self.btn_search_ai)

        self.btn_search_web = LCARSButton("WEB SEARCH", c_tert, shape="pill")
        self.btn_search_web.setMinimumSize(120, 30)
        self.btn_search_web.clicked.connect(lambda checked=False: self._do_search("WEB"))
        search_lay.addWidget(self.btn_search_web)

        self.btn_full_browser = LCARSButton("FULL BROWSER", TitanPalette.Buttons[3], shape="pill")
        self.btn_full_browser.setMinimumSize(120, 30)
        self.btn_full_browser.clicked.connect(self._launch_full_browser)
        search_lay.addWidget(self.btn_full_browser)

        lay.addLayout(search_lay)

        # Browser View
        if _WEB_AVAILABLE:
            nav_lay = HBoxLayout()
            nav_lay.setContentsMargins(0, 0, 0, 0)
            nav_lay.setSpacing(5)

            self.btn_back = LCARSButton("◄ BACK", c_sec, shape="pill")
            self.btn_back.clicked.connect(lambda: getattr(self, 'webview') and self.webview.back())
            self.btn_back.setMinimumSize(100, 25)

            self.btn_fwd = LCARSButton("FORWARD ►", c_sec, shape="pill")
            self.btn_fwd.clicked.connect(lambda: getattr(self, 'webview') and self.webview.forward())
            self.btn_fwd.setMinimumSize(100, 25)

            self.btn_reload = LCARSButton("RELOAD ↺", c_tert, shape="pill")
            self.btn_reload.clicked.connect(lambda: getattr(self, 'webview') and self.webview.reload())
            self.btn_reload.setMinimumSize(100, 25)

            nav_lay.addWidget(self.btn_back)
            nav_lay.addWidget(self.btn_fwd)
            nav_lay.addWidget(self.btn_reload)
            nav_lay.addStretch(1)

            lay.addLayout(nav_lay)

            self.webview = Directive.WebView()
            self.page_handler = InterceptingWebEnginePage(self.webview)
            self.webview.setPage(self.page_handler)
            self.webview.setSizePolicy(Chassis.SizePolicy.Policy.Expanding, Chassis.SizePolicy.Policy.Expanding)
            self.webview.setStyleSheet("background: black;")
            lay.addWidget(self.webview, 1)

            self.webview.setUrl(Directive.Url("https://www.youtube.com/live"))
        else:
            fallback = Visual.Label("QWebEngineView NOT AVAILABLE.\nPlease install PyQt6-WebEngine.")
            fallback.setAlignment(Directive.Align.AlignCenter)
            fallback.setStyleSheet(f"color: {c_tert}; {FontStyle(24, 'bold')};")
            lay.addWidget(fallback, 1)
            self.webview = None

    def _do_search(self, mode="WEB"):
        if not self.webview:
            return
            
        q = self.search_input.text().strip()
        if not q:
            return
            
        # Is it a direct URL or IP?
        import re
        is_url = re.match(r"^(https?://|acestream://|www\.)[^\s]+$|^.*?\.[a-zA-Z]{2,}(/.*)?$", q)
        if is_url and " " not in q:
            if not q.startswith("http") and not q.startswith("acestream"):
                q = "https://" + q
            self._on_search_result(q)
            return

        if mode == "WEB":
            self._on_search_result(f"https://duckduckgo.com/?q={q.replace(' ', '+')}&ia=web")
            return
            
        self.search_input.setEnabled(False)
        self.btn_search_ai.setText("SEARCHING...")
        
        # PROXY FALLBACK (If AI fails or is offline)
        # We'll use a specific thread to fetch an acestream link using a basic DuckDuckGo HTML scaper
        def programmatic_acestream_search():
            import urllib.request
            import urllib.parse
            import re
            print(f"[DEBUG] Running programmatic AceStream scraper fallback for '{q}'...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            def fetch_html(url):
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as response:
                        return response.read().decode('utf-8', errors='ignore')
                except Exception as e:
                    print(f"[AceScraper] Failed to fetch {url}: {e}")
                    return ""
            
            try:
                # 1. First attempt: Search DuckDuckGo specifically for acestream IDs mapped with the teams
                search_query = urllib.parse.quote(f"{q} acestream")
                ddg_url = f"https://html.duckduckgo.com/html/?q={search_query}"
                ddg_html = fetch_html(ddg_url)
                
                # Look for explicit acestream:// links in the results
                aces = re.findall(r'acestream://([a-fA-F0-9]{40})', ddg_html)
                if aces:
                    return f"acestream://{aces[0]}"
                    
                # Look for 40-character hex strings that might be the hash
                hexes = re.findall(r'\b[a-fA-F0-9]{40}\b', ddg_html)
                if hexes:
                    return f"acestream://{hexes[0]}"
                    
                # 2. Try livetv.sx (using duckduckgo site search as proxy)
                search_query_livetv = urllib.parse.quote(f"site:livetv.sx {q}")
                livetv_html = fetch_html(f"https://html.duckduckgo.com/html/?q={search_query_livetv}")
                
                # Find links to livetv.sx matches
                links = re.findall(r'href="(.*?)"', livetv_html)
                match_links = [urllib.parse.unquote(l.split('uddg=')[1].split('&')[0]) for l in links if 'uddg=https://livetv.sx/enx/eventinfo/' in l]
                
                if match_links:
                    match_url = match_links[0]
                    print(f"[AceScraper] Found LiveTV event page: {match_url}")
                    event_html = fetch_html(match_url)
                    # Find acestream links on the event page
                    aces = re.findall(r'acestream://([a-fA-F0-9]{40})', event_html)
                    if aces:
                        return f"acestream://{aces[0]}"
                        
            except Exception as e:
                print(f"[DEBUG] Programmatic scraper failed: {e}")
            return "OFFLINE"
            
        
        prompt = (
            f"You are the LCARS global stream AI. The user requested a live broadcast for: '{q}'. "
            "Use your internet knowledge to find the ABSOLUTE BEST URL for this live stream. "
            "Consider platforms like YouTube Live, Twitch, or specialized sports directories. "
            "IMPORTANT: If the user mentions 'acestream' or 'аке стрім' or similar, you MUST find an AceStream ID/URL (acestream://...) for the match. "
            "CRITICAL: YOU MUST RETURN ONLY ONE RAW URL. NO MARKDOWN, NO EXPLANATIONS. EXACTLY 'https://...' or 'acestream://...'"
        )
        
        # We use a custom thread to bypass BoardComputer command interceptors
        self.search_thread = AISearchThread(self.computer, prompt)
        
        def _intercept_response(res):
            if "OFFLINE" in res or "БЕКЕНД: OFFLINE" in res:
                # Run the scraper
                print("[DEBUG] AI is offline, attempting programmatic scraper...")
                import threading
                def _scrape_and_emit():
                    scraped_res = programmatic_acestream_search()
                    self._on_search_result(scraped_res)
                threading.Thread(target=_scrape_and_emit, daemon=True).start()
            else:
                self._on_search_result(res)
                
        self.search_thread.result_ready.connect(_intercept_response)
        self.search_thread.start()
        
    def _on_search_result(self, response: str):
        self.search_input.setEnabled(True)
        if hasattr(self, 'btn_search_ai'):
            self.btn_search_ai.setText("AI SEARCH")
        
        url = response.strip()
        # Clean up in case the LLM returned markdown links or quotes
        if url.startswith("```"):
            url = url.replace("```", "").replace("\n", "").strip()
        if url.startswith('"') and url.endswith('"'):
            url = url[1:-1]
        
        # Determine if offline message was returned or invalid format
        if "OFFLINE" in url.upper() or "БЕКЕНД: OFFLINE" in url or (not url.startswith("http") and not url.startswith("acestream")):
            q = self.search_input.text().strip()
            # If AI is offline or failed, default to standard Web Search (DuckDuckGo or Google)
            print(f"[DEBUG] Invalid AI response / Offline. Falling back to explicit Web Search for: {q}")
            url = f"https://duckduckgo.com/?q={q.replace(' ', '+')}&ia=web"
            
        # --- Native Ace Stream Integration ---
        if url.startswith("acestream://"):
            hash_id = url.replace("acestream://", "").split("/")[0].strip()
            print(f"[DEBUG] Intercepted AceStream. Formatting for local proxy: {hash_id}")
            # Standard Ace Stream Engine local proxy output
            url = f"http://127.0.0.1:6878/ace/getstream?id={hash_id}"
            
        print(f"[DEBUG] Setting webview URL to: {url}")
        self.webview.setUrl(Directive.Url(url))
        
    def _launch_full_browser(self):
        try:
            from programs.browser import launch as launch_browser
            launch_browser()
        except Exception:
            # Fallback if import path changed
            try:
                import sys
                from pathlib import Path
                br_path = Path(__file__).parent.parent / "lcars_web_browser.py"
                import subprocess
                subprocess.Popen([sys.executable, str(br_path)])
            except Exception as e:
                print(f"[DEBUG] Failed to launch external browser: {e}")
        
    def stop_all(self):
        if self.webview:
            # Just stop any active video by navigating to blank or about:blank
            self.webview.setUrl(Directive.Url("about:blank"))
