/**
 * @author ciju cherian (mail.ciju.cherian@gmail.com)
 *
 * Provides hierarchical pie charts for client side. Needs data
 * in a hierarchical format.
 *
 * @requires jquery, raphael
 * @implements phChart
 * @implements phTimeline
 */

// todo: the event line. including the start pointer etc.
// todo: labels, how to put them. and how to show the % info and the actual milliseconfs info etc.
// todo: auto coloring is another problem. the largest once show darker color and the smaller lighter.
// todo: remove the dependence on jquery.

var plot_fns = function ($, g, log, Raphael){

    g.phTimeline = (function () {
        var options = {
            div:
            '<div id="{phtimeline_id}" style="position:relative">'+
                '  <div class="label" style="height:300px;float:right"></div>' +
                '  <div class="timeline"' +
                '       style="width:500px;height:300px;float:right">' +
                '  </div>' +
                '</div>',
            div_id_tmpl: '{phtimeline_id}',
            label_sel: ':first-child',
            timeline_sel:':last-child',
            div_id: 'ph_timeline'
        };

        // it should take care of creating divs for both the mail
        // graph and the label. label should come above the
        // table. So, that there is no color interference. One also
        // needs to pass in the id or the element to which this has
        // to be put in.

        /**
         * phTimeline: function takes the data, as a csv to show with
         * the dygraph library.
         */

        // todo: have to put the labels in some decent way, probably
        // limit the number of labels to 10 or something. This has to
        // be configurable. Simultaneously, allow those to be
        // shown/hidden dynamically.
        return (function (data) {
            
            var opts = $.extend({}, options, data),
                timeline_div,
                label_div,
                ph_timeline = $(opts.div.replace(opts.div_id_tmpl,
                                                 opts.div_id)),
                g;

            // todo: check for unique id, ex: should not override
            // existing id.

            timeline_div = ph_timeline.find(options.timeline_sel);
            label_div = ph_timeline.find(options.label_sel);
            new Dygraph(timeline_div.get(0),
                        opts.csv, {
                            labels: opts.labels,
                            labelsDiv: label_div && label_div.get(0),
                            labelsWidth: 250,
                            labelsSeparateLines: true,
                            // labelsShowZeroValues: false,
                            xAxisLabelFormater: function (d, gran) {
                                return Dygraph.zeropad(d.getYear()) + '/' +
                                    Dygraph.zeropad(d.getMonth()) + '/' +
                                    Dygraph.zeropad(d.getDate()) + ' ' +
                                    Dygraph.zeropad(d.getHour()) + ':00';
                                // return Dygraph.dateAxisFormatter(new)
                            }
                        });
            return ph_timeline;
        });
    })();                         //end - phTimeline

    g.phChart = (function () {
        var options = {
            templates: {
                'main': '<div id="ph-plots"></div>',
                'div': '<div id="perf-hier-plot-{i}">',
                'plot': '<div>',
                'close': '<div style="text-align:right;"><a class="close" href="javascript:;">x</a></div>'
            },
            css: {
                'background-color': 'black',
                'position': 'fixed',
                'top': '5px'
            },
            'stroke': 20,
            'xcenter': 300.001,
            'ycenter': 300.001,
            'color_options':{
                'len'    : 50,
                'center' : 128,
                'width'  : 127,
                'rphase' : 0,
                'gphase' : 0,
                'bphase' : 0,
                'rfreq'  : 1.666,
                'gfreq'  : 2.666,
                'bfreq'  : 3.666
            }
        };


        /**
         * Produces colors for consecutive tabs in a graph.
         *
         * @param opt<object>  options object.
         * @return object with function next_color, to be called when a new color is needed.
         */
        var getColors = (function (){
            
            var start = 155;
            
            /*
             * not used for now.
              */
            function byte2Hex(n) {
                var nybHexString = "0123456789ABCDEF";
                return String(nybHexString.substr((n >> 4) & 0x0F,1)) + nybHexString.substr(n & 0x0F,1);
            };
            function RGB2Color(r,g,b) {
                return '#' + byte2Hex(r) + byte2Hex(g) + byte2Hex(b);
            };
            
            function lerp(value1, value2, amt) {
                return ((value2 - value1) * amt) + value1;
            };
            function ncolorpicker(i) {
                var h = lerp(0.2, 0.65, Math.random()); // Hue changes make a big difference.
                    var s = lerp(0.2, 0.25, Math.random());
                var b = lerp(0.4, 0.95, Math.random());
                
                // var h = lerp(0.6, 0.65, Math.random());
                // var s = lerp(0.2, 0.25, Math.random());
                // var b = lerp(0.4, 0.95, Math.random());

                var rgb = hsv2rgb(h, s, b);
                var ret = RGB2Color(rgb.red, rgb.green, rgb.blue);
                return ret;
            };
            
            /**
              * Adapted from http://www.easyrgb.com/math.html
              *
              * @see http://jsres.blogspot.com/2008/01/convert-hsv-to-rgb-equivalent.html
              */
            function hsv2rgb(h,s,v) {
                // hsv values = 0 - 1, rgb values = 0 - 255
                var r, g, b;
                var RGB = new Array();
                if (s==0) {
                    RGB['red']=RGB['green']=RGB['blue']=Math.round(v*255);
                } else {
                    // h must be < 1
                    var var_h = h * 6;
                    if (var_h==6) var_h = 0;
                    //Or ... var_i = floor( var_h )
                    var var_i = Math.floor( var_h );
                        var var_1 = v*(1-s);
                    var var_2 = v*(1-s*(var_h-var_i));
                    var var_3 = v*(1-s*(1-(var_h-var_i)));

                    switch (var_i) {
                     case 0: r = v;     g = var_3; b = var_1; break;
                     case 1: r = var_2; g = v;     b = var_1; break;
                     case 2: r = var_1; g = v;     b = var_3; break;
                     case 3: r = var_1; g = var_2; b = v;     break;
                     case 4: r = var_3; g = var_1; b = v;     break;
                    default: r = v; g = var_1; b = var_2;
                    }
                    
                    //rgb results = 0 &#247; 255
                    RGB['red']=Math.round(r * 255);
                    RGB['green']=Math.round(g * 255);
                    RGB['blue']=Math.round(b * 255);
                }
                return RGB;
            };
            
            
            function makeColorGradient(opt, i) {
                var red = Math.sin(opt.rfreq*i + opt.rphase) * opt.width + opt.center;
                var grn = Math.sin(opt.gfreq*i + opt.gphase) * opt.width + opt.center;
                var blu = Math.sin(opt.bfreq*i + opt.bphase) * opt.width + opt.center;
                
                return RGB2Color(red,grn,blu);
            };
            /*
             * end - not used for now.
             */
            
            function gradient(opt, i) {
                return '#' + (155 + i*20);
            };
            
            return function (opt) {
                var seq = 0;
                return {
                    'next_color': function(order) {
                        seq = (typeof order != 'undefined') ? order : seq;
                        var rgb = gradient(opt, seq);
                        // rgb = ncolorpicker(seq);
                        seq+=1;
                        if (seq >= opt.len) seq = 0;
                        return rgb;
                        }
                };
            };
        })();
        
        
        var tree_depth = (function () {
            function tdepth(tree, depth) {
                var chlds = tree.childrens
                , max = depth
                , i
                ;

                for (i in chlds) {
                    max = Math.max(max, tdepth(chlds[i], depth+1));
                }

                return max;
            }
            return function (tree) {
                return tdepth(tree, 1);
            };
        })();


        // puts % info to the data hierarchy.
        var prepare = (function () {
            function prep(data) {
                var tmp = []
                , i
                ;

                for (i in data.childrens) {
                    tmp.push(data.childrens[i]);
                }
                // tmp = data.childrens.slice();
                $.each(tmp.sort(function(a, b) { //todo: no jquery
                    return a.val - b.val;
                }).reverse(),
                       function (i, v) {
                           v.order = i;
                       });
                var chlds = data.childrens, chld;
                    // for (var i=0,len=chlds.length; i<len; i++) {
                for (i in chlds) {
                    chld = chlds[i];
                    chld.percent = (chld.val/data.val)*100;
                    prep(chld);
                }
            }
            return (function (data) { data.percent=100; return prep(data); });
        }());

        function ring(c,x,y,r, sang, dxang, param) {
            var bigger, pirad = Math.PI/180;
            var sx, sy, dx, dy;

            if (dxang == 360) dxang = 359.99; // hack, for circle to be proper.

            bigger = (dxang > 180) ? 1 : 0;

            dxang =  - (sang + dxang);
            sang =  - sang;

            var srad = pirad*sang, drad = pirad*(dxang);
            sx = x+ r*Math.cos(srad);
            sy = y- r*Math.sin(srad);
            dx = x+ r*Math.cos(drad);
            dy = y- r*Math.sin(drad);

            return c.path(['M', sx, sy, 'A', r, r, 0,  bigger, 1, dx, dy]
                          .join(','))
                .attr(param);
        };

        function showTooltip(x, y, contents) {
            $('<div id="tooltip" class="tooltip">' + contents + '</div>').css( {
                display: 'none',
                top: y + 5,
                left: x + 5,
                opacity: 1
            }).appendTo("body").fadeIn('fast');
        };

        // r -> radius, s -> starting angle, e -> ending angle, c -> color.
        function show_childs (data, r, s, pa, colors, raphael) {
            var chldrns       = data.childrens,
                angle_covered = (pa*data.percent)/100,
                color         = colors.next_color(data.order),
                ele;

            ele = ring(raphael, 100.001, 100.001, r, s, angle_covered , {'stroke':color, 'stroke-width':20});


            // ele._gdata = data;
            ele.set_data(data);
            data.element = ele.node;

            // if chlds then for each one show it on the canvas plot.
            // todo: do we need to sort this data.
            if (chldrns != {}) {
                var perc = 0, cr, cs, chld;
                colors = getColors(options.color_options);
                // for (var i=0, len=chldrns.length; i<len; i++) {
                for (var i in chldrns) {
                    chld = chldrns[i];
                    cr = r + 20;          // go to outer layer.
                    cs = s + (perc*angle_covered/100); // start after all the previous childs.
                    arguments.callee.apply(this, [chld, cr, cs, angle_covered, colors, raphael]);
                    perc += chld.percent;
                }
            }
        };

        function plot_data(data, raphael) {
            prepare(data);
            raphael.clear();
            show_childs(data, 10, 0, 360, getColors(options.color_options), raphael);
        }

        Raphael.el.set_data = function (data) {
            this._phdata = data;
        };
        Raphael.el.get_data = function () {
            return this.raphael._phdata;
        };
        Raphael.fn.get_data = function (node) {
            return node.raphael && node.raphael._phdata;
        };


    /**
     * Actual phChart function.
     *
     * @param inp_data : hierarchical representation of data to be
     *                   plotted. Should have integer in 'val' attribute
     *                   and 'name' property with string, and 'childrens'
     *                   property with the childrens of the node.
     * @param hover_cb : callback function to be invoked on mouseover.
     */
    // todo: the close button needs to be optional. The colors
    // need to be shown based on the relative size of particular
    // entry in the ring.
        return function (inp_data, hover_cb, show_x) {
            // initialization and association of functions.
            var colors  = getColors(options.color_options),
                data    = $.extend(true, {}, inp_data), //deep copy
                main    = $(options.templates.main),
                div     = $(options.templates.div.replace(/{i}/g, 1)),
                ele     = $(options.templates.plot.replace(/{i}/g, 1)),
                size    = 0,
                raphael,
                pub_fns;


            if (show_x) {
                $(options.templates.close).appendTo(div);
            }

            // rings * ring size * 2 for sides.
            size = tree_depth(data) * 20 * 2;

            size += 50;
            ele.width(size).height(size);

            raphael = Raphael(ele.get(0), size, size);

            prepare(data);

            // $('body').append( main.append( div.append( ele ) ) );

            main.append( div.append( ele ));

            // todo: have to care about whether raphael is available. could try ninja mode
            // find out how much space is needed. create raphael accordingly at the bottom of the site.
            show_childs(data, 10, 0, 360, colors, raphael);

            pub_fns = {
                get_div: function () {
                    return main;
                },
                get_node: function (path) {
                    return (function (path, node) {
                        var path_nodes = path.split('/');
                            switch (path_nodes.length) {
                             case 0: return null; break;
                             case 1: return node; break;
                            default:
                                if (node.name === path_nodes[0]) {
                                    var chldrns = node.childrens;
                                    // for (var i=0, len=chldrns.length; i<len; i++) {
                                    for (var i in chldrns) {
                                        if (chldrns[i].name === path_nodes[1]) {
                                            return arguments.callee.apply(this, [path_nodes.splice(1).join('/'), chldrns[i]]);
                                        }
                                    }
                                    return null;
                                }
                                break;
                            };
                    })(path, data);
                },                     //get_node finished
                reload: function (inp_data) {
                    data = $.extend(true, {}, inp_data);
                    plot_data(data, raphael);
                },
                reset: function () {
                    plot_data(data, raphael);
                }
            };

            // event handling on the rings.
            $('.close', div).click(function (){
                $(this).parent().parent().remove();
            });

            ele.bind({
                mouseover: function (e) {
                    var target = e.originalTarget || e.target,
                    rap    = raphael.get_data(target);
                    if (rap) {
                        $(this).addClass('clickable');
                        // todo: could use hover callback.
                        showTooltip(e.pageX, e.pageY, rap.name+' perc: '+rap.percent.toFixed(2)+'%  -- val:'+rap.val);
                    }
                },
                mouseout: function (e) {
                    $(this).removeClass('clickable');
                    $('#tooltip').remove();
                },
                click: function (e) {
                    var data = raphael.get_data(e.originalTarget || e.target);
                    if (100 == Math.floor(data.percent)) {
                        pub_fns.reset();
                    } else {
                        plot_data(data, raphael);
                    }
                    }
                });

                // publically available methods.
            return pub_fns;                        //return finishes
        };
    })();

};

plot_fns(jQuery, _phc, function () {}, Raphael);
plot_fns(jQuery, _ph, function () {}, Raphael);


function load_fn() {
    var $ = jQuery,
        log = function () {},
        i;

    // convert date from 'year[-month[-date[-hour]]]' to 'year:month:day hour:min:sec'.
    function process_date(date) {
        var ts = date.split('-'), dpart=[], hpart=[];

        function t2s(t) {
            if (!t) { return '00'; }
            return ( +t < 10 ? '0' : '' ) + t;
        }

        for (i=0; i<3; i++) {       //u
            dpart.push(t2s(ts[i]));
        }
        for (i=3; i<6; i++) {
            hpart.push(t2s(ts[i]));
        }

        return dpart.join('/') + ' ' + hpart.join(':');
        };


    function process_data(data) {
        var hash = {},
        str = '',
        labels = ['dates'],
        i, j, d;

        function hash_entry_to_str(d, a) {
            return [process_date(d), a.join(',')].join(',') + '\n';
        }
        function last_tag(event_str) {
            var lst = event_str.split('/');
            return lst[lst.length-1];
        }
        function process_row(row, hash) {
            var date = row[0];
            // row[1] = cnt.
            // row[2] = total.
            if (!hash[date]) { hash[date] = []; }
            hash[date].push( row[2]/row[1] );
        }

        for (i in data) {
            labels.push( last_tag(i) );
            for (j in data[i]) {
                process_row(data[i][j], hash);
            }
        }

        for (i in hash) {
            str += hash_entry_to_str(i, hash[i]);
        }

        return {labels: labels, csv: str};
    };

    function tree_map(tree, fn) {
        var childs = tree.childrens,
        // len = childs && childs.length || 0,
        c;
        fn(tree);
        // for(c=0; c<len; c++) {
        for (c in childs) {
            tree_map(childs[c], fn);
        }
    }


    // get hierarchical and timeline data simultaneously. and try
    // to show there graphs together. the operation completes when
    // both of them has been shown.
}

jQuery(window).load(load_fn);


