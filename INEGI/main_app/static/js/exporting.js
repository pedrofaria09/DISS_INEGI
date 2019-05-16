/*
 Highcharts JS v6.2.0 (2018-10-17)
 Exporting module

 (c) 2010-2018 Torstein Honsi

 License: www.highcharts.com/license
*/
(function (r) {
    "object" === typeof module && module.exports ? module.exports = r : "function" === typeof define && define.amd ? define(function () {
        return r
    }) : r(Highcharts)
})(function (r) {
    (function (f) {
        var r = f.defaultOptions, t = f.doc, x = f.Chart, p = f.addEvent, J = f.removeEvent, D = f.fireEvent,
            v = f.createElement, E = f.discardElement, F = f.css, y = f.merge, B = f.pick, w = f.each, G = f.objectEach,
            A = f.extend, z = f.win, I = z.navigator.userAgent, H = f.SVGRenderer, K = f.Renderer.prototype.symbols,
            L = /Edge\/|Trident\/|MSIE /.test(I), M = /firefox/i.test(I);
        A(r.lang,
            {
                printChart: "Print chart",
                downloadPNG: "Download PNG image",
                downloadJPEG: "Download JPEG image",
                downloadPDF: "Download PDF document",
                downloadSVG: "Download SVG vector image",
                contextButtonTitle: "Chart context menu"
            });
        r.navigation = {
            buttonOptions: {
                theme: {},
                symbolSize: 14,
                symbolX: 12.5,
                symbolY: 10.5,
                align: "right",
                buttonSpacing: 3,
                height: 22,
                verticalAlign: "top",
                width: 24
            }
        };
        r.exporting = {
            type: "image/png", url: "https://export.highcharts.com/", printMaxWidth: 780, scale: 2, buttons: {
                contextButton: {
                    className: "highcharts-contextbutton",
                    menuClassName: "highcharts-contextmenu",
                    symbol: "menu",
                    titleKey: "contextButtonTitle",
                    menuItems: "printChart separator downloadPNG downloadJPEG downloadPDF downloadSVG".split(" ")
                }
            }, menuItemDefinitions: {
                printChart: {
                    textKey: "printChart", onclick: function () {
                        this.print()
                    }
                }, separator: {separator: !0}, downloadPNG: {
                    textKey: "downloadPNG", onclick: function () {
                        this.exportChart()
                    }
                }, downloadJPEG: {
                    textKey: "downloadJPEG", onclick: function () {
                        this.exportChart({type: "image/jpeg"})
                    }
                }, downloadPDF: {
                    textKey: "downloadPDF", onclick: function () {
                        this.exportChart({type: "application/pdf"})
                    }
                },
                downloadSVG: {
                    textKey: "downloadSVG", onclick: function () {
                        this.exportChart({type: "image/svg+xml"})
                    }
                }
            }
        };
        f.post = function (a, b, c) {
            var d = v("form", y({
                method: "post",
                action: a,
                enctype: "multipart/form-data"
            }, c), {display: "none"}, t.body);
            G(b, function (a, b) {
                v("input", {type: "hidden", name: b, value: a}, null, d)
            });
            d.submit();
            E(d)
        };
        A(x.prototype, {
            sanitizeSVG: function (a, b) {
                if (b && b.exporting && b.exporting.allowHTML) {
                    var c = a.match(/<\/svg>(.*?$)/);
                    c && c[1] && (c = '\x3cforeignObject x\x3d"0" y\x3d"0" width\x3d"' + b.chart.width + '" height\x3d"' +
                        b.chart.height + '"\x3e\x3cbody xmlns\x3d"http://www.w3.org/1999/xhtml"\x3e' + c[1] + "\x3c/body\x3e\x3c/foreignObject\x3e", a = a.replace("\x3c/svg\x3e", c + "\x3c/svg\x3e"))
                }
                return a = a.replace(/zIndex="[^"]+"/g, "").replace(/symbolName="[^"]+"/g, "").replace(/jQuery[0-9]+="[^"]+"/g, "").replace(/url\(("|&quot;)(\S+)("|&quot;)\)/g, "url($2)").replace(/url\([^#]+#/g, "url(#").replace(/<svg /, '\x3csvg xmlns:xlink\x3d"http://www.w3.org/1999/xlink" ').replace(/ (|NS[0-9]+\:)href=/g, " xlink:href\x3d").replace(/\n/, " ").replace(/<\/svg>.*?$/,
                    "\x3c/svg\x3e").replace(/(fill|stroke)="rgba\(([ 0-9]+,[ 0-9]+,[ 0-9]+),([ 0-9\.]+)\)"/g, '$1\x3d"rgb($2)" $1-opacity\x3d"$3"').replace(/&nbsp;/g, "\u00a0").replace(/&shy;/g, "\u00ad")
            }, getChartHTML: function () {
                this.inlineStyles();
                return this.container.innerHTML
            }, getSVG: function (a) {
                var b, c, d, u, k, g = y(this.options, a);
                c = v("div", null, {
                    position: "absolute",
                    top: "-9999em",
                    width: this.chartWidth + "px",
                    height: this.chartHeight + "px"
                }, t.body);
                d = this.renderTo.style.width;
                k = this.renderTo.style.height;
                d = g.exporting.sourceWidth ||
                    g.chart.width || /px$/.test(d) && parseInt(d, 10) || 600;
                k = g.exporting.sourceHeight || g.chart.height || /px$/.test(k) && parseInt(k, 10) || 400;
                A(g.chart, {animation: !1, renderTo: c, forExport: !0, renderer: "SVGRenderer", width: d, height: k});
                g.exporting.enabled = !1;
                delete g.data;
                g.series = [];
                w(this.series, function (a) {
                    u = y(a.userOptions, {
                        animation: !1,
                        enableMouseTracking: !1,
                        showCheckbox: !1,
                        visible: a.visible
                    });
                    u.isInternal || g.series.push(u)
                });
                w(this.axes, function (a) {
                    a.userOptions.internalKey || (a.userOptions.internalKey = f.uniqueKey())
                });
                b = new f.Chart(g, this.callback);
                a && w(["xAxis", "yAxis", "series"], function (d) {
                    var e = {};
                    a[d] && (e[d] = a[d], b.update(e))
                });
                w(this.axes, function (a) {
                    var d = f.find(b.axes, function (b) {
                        return b.options.internalKey === a.userOptions.internalKey
                    }), e = a.getExtremes(), c = e.userMin, e = e.userMax;
                    d && (void 0 !== c && c !== d.min || void 0 !== e && e !== d.max) && d.setExtremes(c, e, !0, !1)
                });
                d = b.getChartHTML();
                D(this, "getSVG", {chartCopy: b});
                d = this.sanitizeSVG(d, g);
                g = null;
                b.destroy();
                E(c);
                return d
            }, getSVGForExport: function (a, b) {
                var c = this.options.exporting;
                return this.getSVG(y({chart: {borderRadius: 0}}, c.chartOptions, b, {
                    exporting: {
                        sourceWidth: a && a.sourceWidth || c.sourceWidth,
                        sourceHeight: a && a.sourceHeight || c.sourceHeight
                    }
                }))
            }, exportChart: function (a, b) {
                b = this.getSVGForExport(a, b);
                a = y(this.options.exporting, a);
                f.post(a.url, {
                    filename: a.filename || "chart",
                    type: a.type,
                    width: a.width || 0,
                    scale: a.scale,
                    svg: b
                }, a.formAttributes)
            }, print: function () {
                var a = this, b = a.container, c = [], d = b.parentNode, f = t.body, k = f.childNodes,
                    g = a.options.exporting.printMaxWidth, e, l;
                if (!a.isPrinting) {
                    a.isPrinting =
                        !0;
                    a.pointer.reset(null, 0);
                    D(a, "beforePrint");
                    if (l = g && a.chartWidth > g) e = [a.options.chart.width, void 0, !1], a.setSize(g, void 0, !1);
                    w(k, function (a, b) {
                        1 === a.nodeType && (c[b] = a.style.display, a.style.display = "none")
                    });
                    f.appendChild(b);
                    setTimeout(function () {
                        z.focus();
                        z.print();
                        setTimeout(function () {
                            d.appendChild(b);
                            w(k, function (a, b) {
                                1 === a.nodeType && (a.style.display = c[b])
                            });
                            a.isPrinting = !1;
                            l && a.setSize.apply(a, e);
                            D(a, "afterPrint")
                        }, 1E3)
                    }, 1)
                }
            }, contextMenu: function (a, b, c, d, u, k, g) {
                var e = this, l = e.chartWidth, n =
                    e.chartHeight, q = "cache-" + a, h = e[q], m = Math.max(u, k), C;
                h || (e.exportContextMenu = e[q] = h = v("div", {className: a}, {
                    position: "absolute",
                    zIndex: 1E3,
                    padding: m + "px",
                    pointerEvents: "auto"
                }, e.fixedDiv || e.container), C = v("div", {className: "highcharts-menu"}, null, h), h.hideMenu = function () {
                    F(h, {display: "none"});
                    g && g.setState(0);
                    e.openMenu = !1;
                    f.clearTimeout(h.hideTimer)
                }, e.exportEvents.push(p(h, "mouseleave", function () {
                    h.hideTimer = setTimeout(h.hideMenu, 500)
                }), p(h, "mouseenter", function () {
                    f.clearTimeout(h.hideTimer)
                }), p(t,
                    "mouseup", function (b) {
                        e.pointer.inClass(b.target, a) || h.hideMenu()
                    }), p(h, "click", function () {
                    e.openMenu && h.hideMenu()
                })), w(b, function (a) {
                    "string" === typeof a && (a = e.options.exporting.menuItemDefinitions[a]);
                    if (f.isObject(a, !0)) {
                        var b;
                        b = a.separator ? v("hr", null, null, C) : v("div", {
                            className: "highcharts-menu-item",
                            onclick: function (b) {
                                b && b.stopPropagation();
                                h.hideMenu();
                                a.onclick && a.onclick.apply(e, arguments)
                            },
                            innerHTML: a.text || e.options.lang[a.textKey]
                        }, null, C);
                        e.exportDivElements.push(b)
                    }
                }), e.exportDivElements.push(C,
                    h), e.exportMenuWidth = h.offsetWidth, e.exportMenuHeight = h.offsetHeight);
                b = {display: "block"};
                c + e.exportMenuWidth > l ? b.right = l - c - u - m + "px" : b.left = c - m + "px";
                d + k + e.exportMenuHeight > n && "top" !== g.alignOptions.verticalAlign ? b.bottom = n - d - m + "px" : b.top = d + k - m + "px";
                F(h, b);
                e.openMenu = !0
            }, addButton: function (a) {
                var b = this, c = b.renderer, d = y(b.options.navigation.buttonOptions, a), f = d.onclick,
                    k = d.menuItems, g, e, l = d.symbolSize || 12;
                b.btnCount || (b.btnCount = 0);
                b.exportDivElements || (b.exportDivElements = [], b.exportSVGElements = []);
                if (!1 !== d.enabled) {
                    var n = d.theme, q = n.states, h = q && q.hover, q = q && q.select, m;
                    delete n.states;
                    f ? m = function (a) {
                        a && a.stopPropagation();
                        f.call(b, a)
                    } : k && (m = function (a) {
                        a && a.stopPropagation();
                        b.contextMenu(e.menuClassName, k, e.translateX, e.translateY, e.width, e.height, e);
                        e.setState(2)
                    });
                    d.text && d.symbol ? n.paddingLeft = B(n.paddingLeft, 25) : d.text || A(n, {
                        width: d.width,
                        height: d.height,
                        padding: 0
                    });
                    e = c.button(d.text, 0, 0, m, n, h, q).addClass(a.className).attr({title: B(b.options.lang[d._titleKey || d.titleKey], "")});
                    e.menuClassName =
                        a.menuClassName || "highcharts-menu-" + b.btnCount++;
                    d.symbol && (g = c.symbol(d.symbol, d.symbolX - l / 2, d.symbolY - l / 2, l, l, {
                        width: l,
                        height: l
                    }).addClass("highcharts-button-symbol").attr({zIndex: 1}).add(e));
                    e.add(b.exportingGroup).align(A(d, {width: e.width, x: B(d.x, b.buttonOffset)}), !0, "spacingBox");
                    b.buttonOffset += (e.width + d.buttonSpacing) * ("right" === d.align ? -1 : 1);
                    b.exportSVGElements.push(e, g)
                }
            }, destroyExport: function (a) {
                var b = a ? a.target : this;
                a = b.exportSVGElements;
                var c = b.exportDivElements, d = b.exportEvents, u;
                a &&
                (w(a, function (a, d) {
                    a && (a.onclick = a.ontouchstart = null, u = "cache-" + a.menuClassName, b[u] && delete b[u], b.exportSVGElements[d] = a.destroy())
                }), a.length = 0);
                b.exportingGroup && (b.exportingGroup.destroy(), delete b.exportingGroup);
                c && (w(c, function (a, d) {
                    f.clearTimeout(a.hideTimer);
                    J(a, "mouseleave");
                    b.exportDivElements[d] = a.onmouseout = a.onmouseover = a.ontouchstart = a.onclick = null;
                    E(a)
                }), c.length = 0);
                d && (w(d, function (a) {
                    a()
                }), d.length = 0)
            }
        });
        H.prototype.inlineToAttributes = "fill stroke strokeLinecap strokeLinejoin strokeWidth textAnchor x y".split(" ");
        H.prototype.inlineBlacklist = [/-/, /^(clipPath|cssText|d|height|width)$/, /^font$/, /[lL]ogical(Width|Height)$/, /perspective/, /TapHighlightColor/, /^transition/, /^length$/];
        H.prototype.unstyledElements = ["clipPath", "defs", "desc"];
        x.prototype.inlineStyles = function () {
            function a(a) {
                return a.replace(/([A-Z])/g, function (a, b) {
                    return "-" + b.toLowerCase()
                })
            }

            function b(c) {
                function h(b, g) {
                    p = v = !1;
                    if (k) {
                        for (t = k.length; t-- && !v;) v = k[t].test(g);
                        p = !v
                    }
                    "transform" === g && "none" === b && (p = !0);
                    for (t = f.length; t-- && !p;) p = f[t].test(g) ||
                        "function" === typeof b;
                    p || u[g] === b && "svg" !== c.nodeName || e[c.nodeName][g] === b || (-1 !== d.indexOf(g) ? c.setAttribute(a(g), b) : r += a(g) + ":" + b + ";")
                }

                var m, u, r = "", q, p, v, t;
                if (1 === c.nodeType && -1 === g.indexOf(c.nodeName)) {
                    m = z.getComputedStyle(c, null);
                    u = "svg" === c.nodeName ? {} : z.getComputedStyle(c.parentNode, null);
                    e[c.nodeName] || (l = n.getElementsByTagName("svg")[0], q = n.createElementNS(c.namespaceURI, c.nodeName), l.appendChild(q), e[c.nodeName] = y(z.getComputedStyle(q, null)), "text" === c.nodeName && delete e.text.fill, l.removeChild(q));
                    if (M || L) for (var x in m) h(m[x], x); else G(m, h);
                    r && (m = c.getAttribute("style"), c.setAttribute("style", (m ? m + ";" : "") + r));
                    "svg" === c.nodeName && c.setAttribute("stroke-width", "1px");
                    "text" !== c.nodeName && w(c.children || c.childNodes, b)
                }
            }

            var c = this.renderer, d = c.inlineToAttributes, f = c.inlineBlacklist, k = c.inlineWhitelist,
                g = c.unstyledElements, e = {}, l, n, c = t.createElement("iframe");
            F(c, {width: "1px", height: "1px", visibility: "hidden"});
            t.body.appendChild(c);
            n = c.contentWindow.document;
            n.open();
            n.write('\x3csvg xmlns\x3d"http://www.w3.org/2000/svg"\x3e\x3c/svg\x3e');
            n.close();
            b(this.container.querySelector("svg"));
            l.parentNode.removeChild(l)
        };
        K.menu = function (a, b, c, d) {
            return ["M", a, b + 2.5, "L", a + c, b + 2.5, "M", a, b + d / 2 + .5, "L", a + c, b + d / 2 + .5, "M", a, b + d - 1.5, "L", a + c, b + d - 1.5]
        };
        x.prototype.renderExporting = function () {
            var a = this, b = a.options.exporting, c = b.buttons, d = a.isDirtyExporting || !a.exportSVGElements;
            a.buttonOffset = 0;
            a.isDirtyExporting && a.destroyExport();
            d && !1 !== b.enabled && (a.exportEvents = [], a.exportingGroup = a.exportingGroup || a.renderer.g("exporting-group").attr({zIndex: 3}).add(),
                G(c, function (b) {
                    a.addButton(b)
                }), a.isDirtyExporting = !1);
            p(a, "destroy", a.destroyExport)
        };
        p(x, "init", function () {
            var a = this;
            w(["exporting", "navigation"], function (b) {
                a[b] = {
                    update: function (c, d) {
                        a.isDirtyExporting = !0;
                        y(!0, a.options[b], c);
                        B(d, !0) && a.redraw()
                    }
                }
            })
        });
        x.prototype.callbacks.push(function (a) {
            a.renderExporting();
            p(a, "redraw", a.renderExporting)
        })
    })(r)
});
//# sourceMappingURL=exporting.js.map