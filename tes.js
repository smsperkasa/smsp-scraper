(self.webpackChunktradingview = self.webpackChunktradingview || []).push([[24081], {
    24654: e => {
        "use strict";
        e.exports = function(e) {
            for (var t = [], n = e.length, r = 0; r < n; r++) {
                var i = e.charCodeAt(r);
                if (i >= 55296 && i <= 56319 && n > r + 1) {
                    var a = e.charCodeAt(r + 1);
                    a >= 56320 && a <= 57343 && (i = 1024 * (i - 55296) + a - 56320 + 65536,
                    r += 1)
                }
                i < 128 ? t.push(i) : i < 2048 ? (t.push(i >> 6 | 192),
                t.push(63 & i | 128)) : i < 55296 || i >= 57344 && i < 65536 ? (t.push(i >> 12 | 224),
                t.push(i >> 6 & 63 | 128),
                t.push(63 & i | 128)) : i >= 65536 && i <= 1114111 ? (t.push(i >> 18 | 240),
                t.push(i >> 12 & 63 | 128),
                t.push(i >> 6 & 63 | 128),
                t.push(63 & i | 128)) : t.push(239, 191, 189)
            }
            return new Uint8Array(t).buffer
        }
    }
    ,
    9995: (e, t, n) => {
        var r = n(939340);
        e.exports = function(e) {
            return e = r(e ^= e >>> 16, 2246822507),
            e = r(e ^= e >>> 13, 3266489909),
            (e ^= e >>> 16) >>> 0
        }
    }
    ,
    939340: e => {
        "use strict";
        e.exports = Math.imul || function(e, t) {
            var n = 65535 & e
              , r = 65535 & t;
            return n * r + ((e >>> 16 & 65535) * r + n * (t >>> 16 & 65535) << 16 >>> 0) | 0
        }
    }
    ,
    855385: (e, t, n) => {
        var r = n(939340)
          , i = n(9995)
          , a = n(24654)
          , o = new Uint32Array([3432918353, 461845907]);
        function s(e, t) {
            return e << t | e >>> 32 - t
        }
        e.exports = function(e, t) {
            if (t = t ? 0 | t : 0,
            "string" == typeof e && (e = a(e)),
            !(e instanceof ArrayBuffer))
                throw new TypeError("Expected key to be ArrayBuffer or string");
            var n = new Uint32Array([t]);
            return function(e, t) {
                for (var n = e.byteLength / 4 | 0, i = new Uint32Array(e,0,n), a = 0; a < n; a++)
                    i[a] = r(i[a], o[0]),
                    i[a] = s(i[a], 15),
                    i[a] = r(i[a], o[1]),
                    t[0] = t[0] ^ i[a],
                    t[0] = s(t[0], 13),
                    t[0] = r(t[0], 5) + 3864292196
            }(e, n),
            function(e, t) {
                var n = e.byteLength / 4 | 0
                  , i = e.byteLength % 4
                  , a = 0
                  , _ = new Uint8Array(e,4 * n,i);
                switch (i) {
                case 3:
                    a ^= _[2] << 16;
                case 2:
                    a ^= _[1] << 8;
                case 1:
                    a ^= _[0] << 0,
                    a = s(a = r(a, o[0]), 15),
                    a = r(a, o[1]),
                    t[0] = t[0] ^ a
                }
            }(e, n),
            function(e, t) {
                t[0] = t[0] ^ e.byteLength,
                t[0] = i(t[0])
            }(e, n),
            n.buffer
        }
    }
    ,
    261030: (e, t, n) => {
        "use strict";
        n.d(t, {
            CookieSettings: () => r,
            bannerPrivacyPreferenceKey: () => p,
            checkBannerPrivacyPreferenceKey: () => x,
            cookieSettingsChangeEvent: () => c,
            cookieSettingsReady: () => l,
            getCookieSetting: () => P,
            hideBanner: () => T,
            isBannerVisible: () => I,
            notApplicateBanner: () => L,
            setCookieSetting: () => z,
            showBanner: () => A
        });
        var r, i = n(251954), a = n(955273), o = n(49437), s = n(66974), _ = n(181706);
        !function(e) {
            e.Analytics = "analytics",
            e.Advertising = "advertising"
        }(r || (r = {}));
        const c = "cookie_settings_changed"
          , l = (0,
        a.createDeferredPromise)()
          , g = window.location.hostname.split(".")
          , u = (0,
        s.isLocal)() ? "" : "." + g.slice(1, g.length).join(".")
          , d = "cookieBanner"
          , p = (0,
        s.isProd)() ? "cookiePrivacyPreferenceBannerProduction" : "cookiePrivacyPreferenceBannerLocal"
          , h = "accepted"
          , f = "ignored"
          , m = "notApplicable"
          , b = "cookiesSettings"
          , v = "localCookiesSettings"
          , w = "cookiePrivacyPreferenceBanner"
          , y = {
            [r.Analytics]: !1,
            [r.Advertising]: !1
        };
        function k() {
            return o.TVLocalStorage.removeItem(d)
        }
        function S(e) {
            return o.TVLocalStorage.getItem(e) === h || o.TVLocalStorage.getItem(e) === m
        }
        function x() {
            return e = p,
            _.get(e) === h || _.get(e) === m;
            var e
        }
        function T() {
            V(h)
        }
        function A() {
            V(f)
        }
        function L() {
            V(m)
        }
        function V(e) {
            _.set(p, e, 3653, "/", u)
        }
        function I() {
            return _.get(p) === f
        }
        function z(e, t) {
            y[e] = t,
            _.set((0,
            s.isProd)() ? b : v, JSON.stringify(y), 3653, "/", u),
            i.emit(c, e, t)
        }
        function P(e) {
            return y[e]
        }
        function F() {
            return o.TVLocalStorage.removeItem(w)
        }
        !function() {
            const e = _.get((0,
            s.isProd)() ? b : v)
              , t = o.TVLocalStorage.getItem(w)
              , n = o.TVLocalStorage.getItem(b);
            if (e) {
                t && n && (F(),
                o.TVLocalStorage.removeItem(b)),
                S(d) && k();
                try {
                    const t = JSON.parse(e);
                    y[r.Analytics] = (null == t ? void 0 : t[r.Analytics]) || !1,
                    y[r.Advertising] = (null == t ? void 0 : t[r.Advertising]) || !1
                } catch (e) {}
            } else if (S(d) && (z(r.Analytics, !0),
            z(r.Advertising, !0),
            T(),
            k()),
            t && n) {
                const e = JSON.parse(n);
                V(t),
                z(r.Analytics, null == e ? void 0 : e[r.Analytics]),
                z(r.Advertising, null == e ? void 0 : e[r.Advertising]),
                F(),
                o.TVLocalStorage.removeItem(b)
            }
        }()
    }
    ,
    66974: (e, t, n) => {
        "use strict";
        n.r(t),
        n.d(t, {
            environment: () => a,
            getEnvironmentByHost: () => i,
            isDebug: () => _,
            isLocal: () => o,
            isProd: () => s
        });
        const r = new Set(["battle", "staging", "test", "local"]);
        function i(e) {
            return -1 !== ["i18n.tradingview.com", "partial.tradingview.com", "www.tradingview.com", "wwwcn.tradingview.com"].indexOf(e) || -1 !== ["d33t3vvu2t2yu5.cloudfront.net", "dwq4do82y8xi7.cloudfront.net", "s.tradingview.com", "s3.tradingview.com"].indexOf(e) || e.match(/^[a-z]{2}\.tradingview\.com/) || e.match(/prod-[^.]+.tradingview.com/) ? "battle" : e.includes("tradingview.com") || e.includes("staging") ? "staging" : "local"
        }
        function a() {
            const e = self.environment;
            return function(e) {
                r.has(e) || console.warn("Invalid environment " + e)
            }(e),
            e
        }
        function o() {
            return "local" === a()
        }
        function s() {
            return "battle" === a()
        }
        function _() {
            return !s()
        }
    }
    ,
    125226: (e, t, n) => {
        "use strict";
        var r = n(49437).TVLocalStorage
          , i = n(942634).Delegate
          , a = n(855385);
        n(638456);
        var o = new i;
        TradingView.FeatureToggle = {
            force_prefix: "forcefeaturetoggle.",
            onChanged: new i,
            enableFeature: function(e) {
                r.setItem(this.force_prefix + e, "true"),
                o.fire(e)
            },
            disableFeature: function(e) {
                r.setItem(this.force_prefix + e, "false"),
                o.fire(e)
            },
            resetFeature: function(e) {
                r.removeItem(this.force_prefix + e),
                o.fire(e)
            },
            onFeaturesStateChanged: function() {
                return o
            }
        },
        TradingView.isFeatureEnabled = function(e) {
            var t = "featuretoggle_seed";
            function i(e) {
                try {
                    var n = a(e + function() {
                        if (window.user && window.user.id)
                            return window.user.id;
                        var e = r.getItem(t);
                        return null !== e || (e = Math.floor(1e6 * Math.random()),
                        r.setItem(t, e)),
                        e
                    }());
                    return new DataView(n).getUint32(0, !0) / 4294967296
                } catch (e) {
                    return .5
                }
            }
            function s(t) {
                return !("local" !== window.environment || !function(e) {
                    var t = ["address_validation_enabled", "skip_navigation_on_chart", "tick_intervals", "broker_TRADESTATION", "broker_TRADOVATE_dev", "black_friday_mainpage", "black_friday_popup", "datawindow", "trading-fast-renew-oauth-token", "switching_year_to_month_disabled", "default_year_billing_cycle_switcher", "marketing-analytics", "visible_address_fields_by_default", "slow-support-warning", "hide-trading-floating-toolbar", "details_disable_bid_ask", "vat_disabled", "disable_recaptcha_on_signup", "braintree-gopro-in-order-dialog", "braintree-apple-pay", "braintree-google-pay", "braintree-apple-pay-trial", "braintree-google-pay-trial", "braintree-3ds-enabled", "order_presets", "trial_increased_monthly_discounts", "checkout-tvcoins", "checkout-3ds", "checkout-subscriptions", "razorpay-card-tvcoins", "razorpay-card-subscriptions", "razorpay-upi-tvcoins", "razorpay-upi-subscriptions", "dlocal-payments", "hide_gopro_popup_upgrade_button", "tradestation_use_sync_mapper", "broker_id_session", "modular_broker_use_sync_mapper", "oanda-european-accounts-warning", "mobile_show_bottom_panel", "disable_save_settings", "ignore_mobile_apps_distinguish_pro_full_name", "desktop_version_notification_enabled", "favorites-in-broker-dropdown", "hide_ecomonic_events", "mobile_trading_web", "mobile_trading_ios", "mobile_trading_android", "hide_real_brokers_on_mobile", "disable_tradestation_country_block", "enable_trading_server_logger", "hide_ranges_label_colors", "disable_user_specific_encryption", "minds_widget_enabled", "self-replacing-advanced-chart-widget", "disable-calendar-advanced-chart-widget", "disable-lse-data-screener-heatmap-widgets", "symphony_notification_badges", "paper_competition_banner", "paper_competition_started_dialog", "paper_subaccount_custom_currency", "disable_pushstream_connections_for_anonymous_users", "use_staging_verifier", "account_verifier_maintenance", "ibkr_use_new_init_session_api", "tradestation_account_data_streaming", "enable_eventsource_pushstream_transport", "enable_eventsource_pushstream_mobile", "performance_test_mode", "ftx_request_server_logger", "ibkr_request_server_logger", "disallow_concurrent_sessions", "check_ibkr_side_maintenance", "tradestation_request_server_logger", "trading_request_server_logger", "hide_tweet_drawingtool", "hide_anchored_note", "enable_diff_decorations", "disable_pine_v4", "enable_profiler", "pine_logs_in_detach", "editor_new_save", "no_buy_hold_backtesting", "editor_new_save_only", "hide_find_in_header", "backtesting_report", "enable_new_custom_public_chats", "bottom_panel_track_events", "ibkr_ws_account_summary", "continuous_front_contract_trading", "vertex-tax-included", "enable_traded_context_linking", "order_context_validation_in_instant_mode", "show_data_problems_in_help_center", "chart_storage_hibernation_delay_60min", "chart_storage_hibernation_delay_10min", "chart_storage_hibernation_delay_5min", "force_disable_jsx_menu_items_rendering", "hide_dom", "enable_sign_in_popup_with_evercookie", "start_replay_right_after_point_selection", "switching_raf_toast", "new_order_size_calculator", "order_type_specific_settings_saving", "hide_position_trade_value", "paper_force_connect_pushstream", "use_broker_logos_from_single_source", "alerts-start-christmas", "alerts-use-http-caching", "alerts-remove-offline-pop-ups", "alerts-remove-clear-alerts-button", "forexcom_session_v2", "fxcm_server_logger", "minds_comments_enable_for_free_users", "fxcm_trailing_stop_bracket", "mock_tweet_data_for_tests", "replay_result_sharing", "ibkr_ws_server_logger", "options_strategy_analyzer_tab", "options_details_widget", "options_overlay", "options_product_page", "options_exchange_nse", "options_exchange_cme", "options_exchange_cbot", "options_exchange_comex", "options_exchange_nymex", "options_exchange_bse", "options_exchange_opra", "ibkr_subscribe_to_order_updates_first", "rest_logout_on_429", "amp_oauth_authorization", "blueline_oauth_authorization", "dorman_oauth_authorization", "cqg_oauth_authorization", "ironbeam_oauth_authorization", "optimus_oauth_authorization", "stonex_oauth_authorization", "tickmill_oauth_authorization", "ibkr_ws_account_ledger", "force_max_allowed_pulling_intervals", "fxcm_password_authorization_type", "change_password_suggestion_popup", "ibkr_disable_ws_connect_timeout", "oanda_rest_api", "launch-oanda-country-group-1", "launch-oanda-country-group-2", "launch-oanda-country-group-3", "news_enable_streaming", "news_screener_page_client", "news_enable_streaming_hibernation", "news_streaming_hibernation_delay_60min", "news_streaming_hibernation_delay_10min", "news_streaming_hibernation_delay_5min", "replay_trading_brackets", "cqg-realtime-bandwidth-limit", "cityindex_spreadbetting", "paper_use_new_auth", "stack_trace_clickable", "oauth2_code_flow_provider_server_logger", "turn_off_ai", "enable_binanceapis_base_url", "unsibscribe_competition_for_participants", "enable_first_touch_is_selection", "paper_delay_trading", "static_dom", "binance_disable_live_account_verification", "enable_forced_email_confirmation", "ylg_oauth_authorization", "show_replay_trading_panel", "order_ticket_resizable_drawer_on", "enable_toast_notifications_groupable", "enable_order_moving_by_price_line", "replay_trading_on_study", "enable_anchor_for_traded_objects", "snowplow_3", "renew_token_preemption_30", "renew_token_preemption_60", "renew_token_preemption_120", "do_not_open_ot_from_plus_button", "rest_use_async_mapper"]
                      , n = "[A-Z]+[a-zA-Z0-9_]+"
                      , r = new RegExp(`broker_${n}_dev`,"g")
                      , i = new RegExp(`hide_${n}_on_ios`,"g")
                      , a = new RegExp(`hide_${n}_on_android`,"g")
                      , o = new RegExp(`hide_${n}_on_mobile_web`,"g");
                    return -1 === t.indexOf(e) && -1 === e.indexOf("-maintenance") && !1 === r.test(e) && !1 === i.test(e) && !1 === a.test(e) && !1 === o.test(e)
                }(t)) || (!e[t] || -1 !== e[t]) && (!!("true" === r.getItem(TradingView.FeatureToggle.force_prefix + t) || window.is_authenticated && "undefined" != typeof user && user.settings && "true" === user.settings[TradingView.FeatureToggle.force_prefix + t]) || !("false" === r.getItem(TradingView.FeatureToggle.force_prefix + t) || window.is_authenticated && "undefined" != typeof user && user.settings && "false" === user.settings[TradingView.FeatureToggle.force_prefix + t]) && (!!e[t] && (1 === e[t] || i(t) <= e[t])))
            }
            return TradingView.onWidget() || n.e(34604).then(n.bind(n, 262078)).then((t => {
                t.pushStreamMultiplexer.on("featuretoggle", (function(t) {
                    var n = s(t.name);
                    e[t.name] = t.state,
                    n !== s(t.name) && o.fire(t.name)
                }
                ))
            }
            )),
            s
        }(window.featureToggleState || {}),
        t.FeatureToggle = TradingView.FeatureToggle,
        t.isFeatureEnabled = TradingView.isFeatureEnabled,
        t.onFeaturesStateChanged = TradingView.FeatureToggle.onFeaturesStateChanged.bind(TradingView.FeatureToggle)
    }
    ,
    49437: (e, t, n) => {
        "use strict";
        const {getLogger: r} = n(338619)
          , i = r("TVLocalStorage");
        var a = function() {
            try {
                this.isAvailable = !0,
                this.localStorage = window.localStorage,
                this.localStorage.setItem("tvlocalstorage.available", "true")
            } catch (e) {
                delete this.isAvailable,
                delete this.localStorage
            }
            this._updateLength();
            try {
                this._report()
            } catch (e) {}
        };
        a.prototype._report = function() {
            if (this.isAvailable) {
                const e = 10
                  , t = [];
                for (let e = 0; e < this.localStorage.length; e++) {
                    const n = this.key(e);
                    t.push({
                        key: n,
                        length: String(this.getItem(n)).length
                    })
                }
                t.sort(( (e, t) => t.length - e.length));
                const n = t.slice(0, e);
                t.sort(( (e, t) => t.key.length - e.key.length));
                const r = t.slice(0, e);
                i.logNormal(`Total amount of keys in Local Storage: ${this.length}`),
                i.logNormal(`Top ${e} keys with longest values: ${JSON.stringify(n)}`),
                i.logNormal(`Top ${e} longest key names: ${JSON.stringify(r)}`);
                try {
                    navigator.storage.estimate().then((e => {
                        i.logNormal(`Storage estimate: ${JSON.stringify(e)}`)
                    }
                    ))
                } catch (e) {}
            }
        }
        ,
        a.prototype.length = 0,
        a.prototype.isAvailable = !1,
        a.prototype.localStorage = {
            "tvlocalstorage.available": "false"
        },
        a.prototype._updateLength = function() {
            if (this.isAvailable)
                this.length = this.localStorage.length;
            else {
                var e, t = 0;
                for (e in this.localStorage)
                    this.localStorage.hasOwnProperty(e) && t++;
                this.length = t
            }
        }
        ,
        a.prototype.key = function(e) {
            return this.isAvailable ? this.localStorage.key(e) : Object.keys(this.localStorage)[e]
        }
        ,
        a.prototype.getItem = function(e) {
            return this.isAvailable ? this.localStorage.getItem(e) : void 0 === this.localStorage[e] ? null : this.localStorage[e]
        }
        ,
        a.prototype.setItem = function(e, t) {
            this.isAvailable ? this.localStorage.setItem(e, t) : this.localStorage[e] = t,
            this._updateLength()
        }
        ,
        a.prototype.removeItem = function(e) {
            this.isAvailable ? this.localStorage.removeItem(e) : delete this.localStorage[e],
            this._updateLength()
        }
        ,
        a.prototype.clear = function() {
            this.isAvailable ? this.localStorage.clear() : this.localStorage = {},
            this._updateLength()
        }
        ,
        window.TVLocalStorage = new a,
        e.exports.TVLocalStorage = window.TVLocalStorage
    }
    ,
    955273: (e, t, n) => {
        "use strict";
        function r() {
            let e, t;
            return {
                promise: new Promise(( (n, r) => {
                    e = n,
                    t = r
                }
                )),
                reject: t,
                resolve: e
            }
        }
        n.d(t, {
            createDeferredPromise: () => r
        })
    }
}]);
