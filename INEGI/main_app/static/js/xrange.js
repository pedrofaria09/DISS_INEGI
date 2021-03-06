/*
 Highcharts JS v6.2.0 (2018-10-17)
 X-range series

 (c) 2010-2018 Torstein Honsi, Lars A. V. Cabrera

 License: www.highcharts.com/license
*/
(function (e) {
    "object" === typeof module && module.exports ? module.exports = e : "function" === typeof define && define.amd ? define(function () {
        return e
    }) : e(Highcharts)
})(function (e) {
    (function (c) {
        var e = c.addEvent, t = c.defined, n = c.seriesTypes.column, k = c.each, u = c.isNumber, v = c.isObject,
            p = c.merge, q = c.pick, w = c.seriesType, x = c.Axis, m = c.Point, y = c.Series;
        w("xrange", "column", {
            colorByPoint: !0,
            dataLabels: {
                verticalAlign: "middle", inside: !0, formatter: function () {
                    var a = this.point.partialFill;
                    v(a) && (a = a.amount);
                    t(a) || (a = 0);
                    return 100 *
                        a + "%"
                }
            },
            tooltip: {
                headerFormat: '\x3cspan style\x3d"font-size: 0.85em"\x3e{point.x} - {point.x2}\x3c/span\x3e\x3cbr/\x3e',
                pointFormat: '\x3cspan style\x3d"color:{point.color}"\x3e\u25cf\x3c/span\x3e {series.name}: \x3cb\x3e{point.yCategory}\x3c/b\x3e\x3cbr/\x3e'
            },
            borderRadius: 3,
            pointRange: 0
        }, {
            type: "xrange",
            parallelArrays: ["x", "x2", "y"],
            requireSorting: !1,
            animate: c.seriesTypes.line.prototype.animate,
            cropShoulder: 1,
            getExtremesFromAll: !0,
            autoIncrement: c.noop,
            getColumnMetrics: function () {
                function a() {
                    k(l.series,
                        function (a) {
                            var b = a.xAxis;
                            a.xAxis = a.yAxis;
                            a.yAxis = b
                        })
                }

                var b, l = this.chart;
                a();
                b = n.prototype.getColumnMetrics.call(this);
                a();
                return b
            },
            cropData: function (a, b, l, d) {
                b = y.prototype.cropData.call(this, this.x2Data, b, l, d);
                b.xData = a.slice(b.start, b.end);
                return b
            },
            translatePoint: function (a) {
                var b = this.xAxis, l = this.yAxis, d = this.columnMetrics, f = this.options, g = f.minPointLength || 0,
                    c = a.plotX, h = q(a.x2, a.x + (a.len || 0)), e = b.translate(h, 0, 0, 0, 1), h = Math.abs(e - c),
                    k = this.chart.inverted, m = q(f.borderWidth, 1) % 2 / 2, n = d.offset,
                    r = Math.round(d.width);
                g && (g -= h, 0 > g && (g = 0), c -= g / 2, e += g / 2);
                c = Math.max(c, -10);
                e = Math.min(Math.max(e, -10), b.len + 10);
                t(a.options.pointWidth) && (n -= (Math.ceil(a.options.pointWidth) - r) / 2, r = Math.ceil(a.options.pointWidth));
                f.pointPlacement && u(a.plotY) && l.categories && (a.plotY = l.translate(a.y, 0, 1, 0, 1, f.pointPlacement));
                a.shapeArgs = {
                    x: Math.floor(Math.min(c, e)) + m,
                    y: Math.floor(a.plotY + n) + m,
                    width: Math.round(Math.abs(e - c)),
                    height: r,
                    r: this.options.borderRadius
                };
                f = a.shapeArgs.x;
                g = f + a.shapeArgs.width;
                0 > f || g > b.len ? (f =
                    Math.min(b.len, Math.max(0, f)), g = Math.max(0, Math.min(g, b.len)), b = g - f, a.dlBox = p(a.shapeArgs, {
                    x: f,
                    width: g - f,
                    centerX: b ? b / 2 : null
                })) : a.dlBox = null;
                a.tooltipPos[0] += k ? 0 : h / 2;
                a.tooltipPos[1] -= k ? -h / 2 : d.width / 2;
                if (b = a.partialFill) v(b) && (b = b.amount), u(b) || (b = 0), d = a.shapeArgs, a.partShapeArgs = {
                    x: d.x,
                    y: d.y,
                    width: d.width,
                    height: d.height,
                    r: this.options.borderRadius
                }, a.clipRectArgs = {
                    x: d.x,
                    y: d.y,
                    width: Math.max(Math.round(h * b + (a.plotX - c)), 0),
                    height: d.height
                };
                l.categories && (a.category = l.categories[a.y])
            },
            translate: function () {
                n.prototype.translate.apply(this,
                    arguments);
                k(this.points, function (a) {
                    this.translatePoint(a)
                }, this)
            },
            drawPoint: function (a, b) {
                var c = this.chart.renderer, d = a.graphic, f = a.shapeType, g = a.shapeArgs, e = a.partShapeArgs,
                    h = a.clipRectArgs;
                if (a.isNull) d && (a.graphic = d.destroy()); else {
                    if (d) a.graphicOriginal[b](p(g)); else a.graphic = d = c.g("point").addClass(a.getClassName()).add(a.group || this.group), a.graphicOriginal = c[f](g).addClass(a.getClassName()).addClass("highcharts-partfill-original").add(d);
                    e && (a.graphicOverlay ? (a.graphicOverlay[b](p(e)), a.clipRect.animate(p(h))) :
                        (a.clipRect = c.clipRect(h.x, h.y, h.width, h.height), a.graphicOverlay = c[f](e).addClass("highcharts-partfill-overlay").add(d).clip(a.clipRect)))
                }
            },
            drawPoints: function () {
                var a = this, b = a.getAnimationVerb();
                k(a.points, function (c) {
                    a.drawPoint(c, b)
                })
            },
            getAnimationVerb: function () {
                return this.chart.pointCount < (this.options.animationLimit || 250) ? "animate" : "attr"
            }
        }, {
            applyOptions: function () {
                var a, b = m.prototype.applyOptions.apply(this, arguments);
                a = b.series;
                if (a.options.colorByPoint && !b.options.color) {
                    var c = a.options.colors ||
                        a.chart.options.colors;
                    a = b.y % (c ? c.length : a.chart.options.chart.colorCount);
                    b.options.colorIndex || (b.colorIndex = a)
                }
                return b
            }, init: function () {
                m.prototype.init.apply(this, arguments);
                this.y || (this.y = 0);
                return this
            }, setState: function () {
                m.prototype.setState.apply(this, arguments);
                this.series.drawPoint(this, this.series.getAnimationVerb())
            }, getLabelConfig: function () {
                var a = m.prototype.getLabelConfig.call(this), b = this.series.yAxis.categories;
                a.x2 = this.x2;
                a.yCategory = this.yCategory = b && b[this.y];
                return a
            }, tooltipDateKeys: ["x",
                "x2"], isValid: function () {
                return "number" === typeof this.x && "number" === typeof this.x2
            }
        });
        e(x, "afterGetSeriesExtremes", function () {
            var a = this.series, b, c;
            this.isXAxis && (b = q(this.dataMax, -Number.MAX_VALUE), k(a, function (a) {
                a.x2Data && k(a.x2Data, function (a) {
                    a > b && (b = a, c = !0)
                })
            }), c && (this.dataMax = b))
        })
    })(e)
});
//# sourceMappingURL=xrange.js.map