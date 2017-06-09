$(function(){
	mapboxgl.accessToken = 'pk.eyJ1IjoidGF0dGlpIiwiYSI6ImNqMWFrZ3ZncjAwNmQzM3BmazRtNngxam8ifQ.DNMc6j7E4Gh7UkUAaEAPxA';
	var map = new mapboxgl.Map({
		container: 'map',
		style: 'mapbox://styles/tattii/cj3jrmgsp002i2rt50tobxo27',
		zoom: 5,
		center: [136.6, 35.5]
	});

	var popup = new mapboxgl.Popup({
		closeButton: false
	});

	var show_layer = "city";
	var selected;
	var $sidebar = $("#sidebar");
	var citylist;

	$.get("geodata/list.json", function (data){
		citylist = data;
	});

	map.on("load", function() {
		addVtileLayer(show_layer);

		map.on('mousemove', function(e) {
			var features = map.queryRenderedFeatures(e.point, { layers: ['warning-area-' + show_layer] });
			map.getCanvas().style.cursor = (features.length) ? 'crosshair' : '';

			if (!features.length) {
				popup.remove();
				return;
			}

			var feature = features[0];
			var name_prop = (show_layer == 'city') ? 'name' : show_layer + 'Name';

			popup.setLngLat(e.lngLat)
				.setText(feature.properties[name_prop])
				.addTo(map);
		});

		map.on('click', function(e) {
			var features = map.queryRenderedFeatures(e.point, { layers: ['warning-area-' + show_layer] });
			if (!features.length) return;

			// show selected area on map
			map.getCanvas().style.cursor = 'pointer';
			var code_prop = (show_layer == 'city') ? 'code' : show_layer + 'Code';
			var code = features[0].properties[code_prop];
			map.setFilter("selected-area-" + show_layer, ["==", code_prop, code]);

			// show data on sidebar
			if (!selected || code != selected.code){
				updateSidebar(code, features[0]);
			}

			if ($sidebar.sidebar("is hidden")){
				$sidebar.sidebar('setting', 'transition', 'overlay')
				.sidebar('setting', 'dimPage', false)
				.sidebar('setting', 'closable', false)
				.sidebar('show');
			}

			selected = { feature: features[0], code: code, code_prop: code_prop };
		});
	});

	$("#layer-select button").on("click", function (){
		var $this = $(this);
		if ($this.hasClass("active")) return;

		changeLayer($this.attr("l"));
	});

	$("#sidebar-close").on("click", function(){
		$sidebar.sidebar("hide");
	});

	function changeLayer (layer){
		// .active
		$("#layer-select .active").removeClass("active");
		$("#layer-select [l=" + layer +"]").addClass("active");

		// change layer
		removeVtileLayer(show_layer);
		show_layer = layer;
		addVtileLayer(show_layer);
	}

	function addVtileLayer (layer){
		var source_layer = ((layer == 'city') ? '' : layer) + 'allgeojson';
		var source_suffix = (layer == 'city') ? '' : '-' + layer;

		map.addSource("vtile-" + layer, {
			"type": "vector",
			"minzoom": 0,
			"maxzoom": 10,
			"tiles": ["https://s3-ap-northeast-1.amazonaws.com/vector-tile/warning-area" + source_suffix + "/{z}/{x}/{y}.pbf"],
			"attribution": '<a href="http://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v2_3.html" target="_blank">国土数値情報</a>'
		});

		map.addLayer({
			"id": "warning-area-" + layer,
			"type": "fill",
			"source": "vtile-" + layer,
			"source-layer": source_layer,
			"paint": {
				"fill-color": "rgba(126, 199, 216, 0.4)",
				"fill-outline-color": "rgba(0, 84, 153, 0.7)"
			}
		});

		var filter = ["==", "code", ""];
		if (selected){
			var code_prop = (layer == 'city') ? 'code' : layer + 'Code';
			if (selected.feature && selected.feature.properties[code_prop]){
				// upscale
				filter = ["==", code_prop, selected.feature.properties[code_prop]];
				if ($sidebar.sidebar("is visible")){
					updateSidebar(selected.feature.properties[code_prop], selected.feature);
				}
			}else{
				// downscale
				filter = ["==", selected.code_prop, selected.code];
			}
		}

		map.addLayer({
			"id": "selected-area-" + layer,
			"type": "fill",
			"source": "vtile-" + layer,
			"source-layer": source_layer,
			"paint": {
				"fill-color": "rgba(245, 143, 152, 0.4)",
				"fill-outline-color": "rgba(245, 143, 152, 0.7)"
			},
			"filter": filter
		});
	}

	function removeVtileLayer (layer){
		map.removeLayer("selected-area-" + layer);
		map.removeLayer("warning-area-" + layer);
		map.removeSource("vtile-" + layer);
	}

	function updateSidebar (code, feature){
		var name_prop = (show_layer == 'city') ? 'name' : show_layer + 'Name';
		$("#sidebar-title h2").text(feature.properties[name_prop]);

		var $bread = $("#sidebar-breadcrumb");
		$bread.html("");

		var layers = ['pref', 'distlict', 'division'];
		for (var i in layers){
			var layer = layers[i];
			if (layer == show_layer) break;
			if (feature.properties[layer + 'Name']){
				$bread.append('<a class="section bread-link" layer="' + layer + '" code="' + 
					feature.properties[layer + 'Code'] + '">' + 
					feature.properties[layer + 'Name'] + 
					'</a><i class="right angle icon divider"></i>'
				);
			}
		}

		if (show_layer == "pref"){
			$("#sidebar-title").css("margin-top", "0px");
		}else{
			$("#sidebar-title").css("margin-top", "15px");
		}

		setJMALink(code);

		$("#sidebar-list").html("");
		if (show_layer != "city"){
			updateSidebarList(code);
		}

		$(".bread-link").on("click", function(){
			var $this = $(this);
			var code = $this.attr("code");
			var layer = $this.attr("layer");

			changeLayer(layer);
			updateSidebar(code, feature);

			var feature_up = { properties: {} };
			var layers = ['pref', 'distlict', 'division'];
			for (var i in layers){
				var l = layers[i];
				if (l == layer) break;
				if (feature.properties[l + 'Code']){
					feature_up.properties[l + 'Code'] = feature.properties[l + 'Code']; 
					feature_up.properties[l + 'Name'] = feature.properties[l + 'Name']; 
				}
			}
			var code_prop = (layer == 'city') ? 'code' : layer + 'Code';
			selected = { feature: feature_up, code: code, code_prop: code_prop };

			//map.on('data', function(){
			//	showArea(code);
			//	map.off('data');
			//});
		});
	}

	function setJMALink (code){
		var pcode = parseInt(code.substr(0, 2)), fcode;
		if (pcode == 1){
			fcode = "0" + code.substr(2, 1);
		}else if (pcode == 47){
			fcode = 53 + parseInt(code.substr(3,1));
		}else{
			var jma_pref_code = [
				8, 10, 12, 9, 11, 13, 14, 16, 15, 17, 18, 19, 20, 23, 24, 25, 26, 21, 22, 
				28, 27, 29, 30, 34, 33, 31, 32, 35, 36,
				39, 38, 40, 38, 45, 43, 41, 42, 44,
				46, 47, 48, 49, 50, 51, 52
			];
			fcode = ("0" + jma_pref_code[pcode - 2]).slice(-2);
		}

		if (show_layer == "pref"){
			$("#jma-link a").attr("href", "http://www.jma.go.jp/jp/warn/3" + fcode + ".html");
		}else if (show_layer == "city"){
			$("#jma-link a").attr("href", "http://www.jma.go.jp/jp/warn/f_" + code.substr(0, 6) + "0.html"); 
		}else{
			$("#jma-link a").attr("href", "http://www.jma.go.jp/jp/warn/3" + fcode + "_table.html#" + code);
		}
	}

	function updateSidebarList (code){
		var $list = $("#sidebar-list");
		var pcode = code.substr(0, 4) + "00";
		var dcode = code.substr(0, 5) + "0";
		var showdata, layer;

		if (citylist[code]){
			layer = "pref";
			showdata = citylist[code].data;

		}else if (citylist[pcode]){
			if (citylist[pcode].data[code]){
				layer = "distlict";
				showdata = citylist[pcode].data[code].data;

			}else if (citylist[pcode].data[dcode]){
				layer = "division";
				showdata = citylist[pcode].data[dcode].data[code].data;
			}
		}

		if (!showdata){
			return console.error("not found");
		}

		for (var acode in showdata){
			var d = showdata[acode];
			$list.append('<div class="item"><a class="list-link" code=' + acode + '>' + d.name + '</a></div>');
		}

		$(".list-link").on("click", function(){
			var code = $(this).attr("code");

			var down_layer = { pref: 'distlict', distlict: 'division', division: 'city' };
			var l = down_layer[layer];

			var feature_down = selected.feature;
			var code_prop = (l == 'city') ? 'code' : l + 'Code';
			var name_prop = (l == 'city') ? 'name' : l + 'Name';
			feature_down.properties[code_prop] = code;
			feature_down.properties[name_prop] = $(this).text();
			selected = { feature: feature_down, code: code, code_prop: code_prop };

			changeLayer(l);
			updateSidebar(code, feature_down);

			// request feature update
		});
	}

	function showArea (code){
		var layer = map.getLayer('selected-area-' + show_layer);
		var relatedFeatures = map.querySourceFeatures(layer.source, {
			sourceLayer: layer.sourceLayer,
			filter: layer.filter
		});

		console.log(relatedFeatures[0]);
	}
});
