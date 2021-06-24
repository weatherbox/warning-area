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

	// responsive
	var mobile = $(window).width() < 640;
	if (mobile){
		$('.ui.dropdown').dropdown({
			onChange: function (value){
				changeLayer(value);
			}
		});

	}else{ // pc
		$("#layer-dropdown").hide();
		$("#layer-select").show();
		$("#layer-select button").on("click", function (){
			var $this = $(this);
			if ($this.hasClass("active")) return;

			changeLayer($this.attr("l"));
		});

		$sidebar.removeClass("bottom").addClass("left");
		$("#sidebar-close").show();
		$("#sidebar-close").on("click", function(){
			$sidebar.sidebar("hide");
		});

		$("#sidebar-breadcrumb-pc").show();
		$("#sidebar-breadcrumb").hide();
	}

	map.on("load", function() {
		map.addSource("vtile", {
			"type": "vector",
			"minzoom": 0,
			"maxzoom": 10,
		  "tiles": ["https://weatherbox.github.io/warning-area-vt/v2/{z}/{x}/{y}.pbf"],
		  "attribution": '<a href="https://www.data.jma.go.jp/developer/gis.html" target="_blank">気象庁GISデータ</a>'
		});
		addVtileLayer(show_layer);
		var moving = false, zooming = false; // only pc

		if (mobile){
			map.on('mousemove', selectArea);

		}else{
			map.on('mousemove', hoverArea);
			map.on('click', selectArea);
			map.on('movestart', function (){ moving = true; });
			map.on('moveend', function (){ moving = false; });
			map.on('zoomstart', function (){ zooming = true; });
			map.on('zoomend', function (){ zooming = false; });
		}

		function hoverArea (e){
			if (moving || zooming) return false;
			var features = map.queryRenderedFeatures(e.point, { layers: ['warning-area-' + show_layer] });
			map.getCanvas().style.cursor = (features.length) ? 'crosshair' : '';

			if (!features.length) {
				popup.remove();
				return;
			}

			var feature = features[0];
			popup.setLngLat(e.lngLat)
				.setText(feature.properties.name)
				.addTo(map);
		}

		function selectArea (e){
			var features = map.queryRenderedFeatures(e.point, { layers: ['warning-area-' + show_layer] });

			if (!features.length){
				if (mobile){
					map.setFilter("selected-area-" + show_layer, ["==", "", ""]);
					selected = null;
					$sidebar.sidebar("hide");
				}
				return;
			}

			// show selected area on map
			if (!mobile) map.getCanvas().style.cursor = 'pointer';
			var code_prop = 'code';
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
		}
	});


	function changeLayer (layer){
		// .active
		if (mobile){
			$(".ui.dropdown").dropdown("set selected", layer);

		}else{
			$("#layer-select .active").removeClass("active");
			$("#layer-select [l=" + layer +"]").addClass("active");
		}

		// change layer
		removeVtileLayer(show_layer);
		show_layer = layer;
		addVtileLayer(show_layer);
	}

	function addVtileLayer (layer){
		map.addLayer({
			"id": "warning-area-" + layer,
			"type": "fill",
			"source": "vtile",
			"source-layer": layer,
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
			"source": "vtile",
			"source-layer": layer,
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
	}

  function search(code, layer) {
    if (layer == 'pref') return [];

    var codes = [];
    for (var prefCode in citylist) {
      var pref = citylist[prefCode];
      codes[0] = { name: pref.name, code: prefCode, layer: 'pref' };
      if (layer == 'distlict' && code in pref.data) return codes.slice(0, 1);

      for (var distlictCode in pref.data) {
        var distlict = pref.data[distlictCode];
        codes[1] = { name: distlict.name, code: distlictCode, layer: 'distlict' };
        if (layer == 'division' && code in distlict.data) return codes.slice(0, 2);

        for (var divisionCode in distlict.data) {
          var division = distlict.data[divisionCode];
          codes[2] = { name: division.name, code: divisionCode, layer: 'division' };
          if (code in division.data) return codes;
        }
      }
    }

  }

	function updateSidebar (code, feature, wlayer){
		var name_prop = 'name';
		$("#sidebar-title h2").text(feature.properties[name_prop]);

		var $bread = (mobile) ? $("#sidebar-breadcrumb") : $("#sidebar-breadcrumb-pc");
		$bread.html("");

    var tree = search(code, show_layer);
		for (var i in tree){
			if (feature.properties['name']){
				$bread.append('<a class="section bread-link" layer="' + tree[i].layer + '" code="' + 
					tree[i].code + '">' + 
					tree[i].name + 
					'</a><i class="right angle icon divider"></i>'
				);
			}
		}

		if (mobile){
			if (show_layer == "pref"){
				$bread.hide();
				$("#sidebar-title").css("margin-bottom", "0px");
			}else{
				$bread.show();
				$("#sidebar-title").css("margin-bottom", "8px");
			}
		}else{
			if (show_layer == "pref"){
				$("#sidebar-title").css("margin-top", "0px");
			}else{
				$("#sidebar-title").css("margin-top", "15px");
			}
		}

		setJMALink(code);

		$("#sidebar-list").html("");
		if (show_layer != "city"){
			$("#list-accordion").show();
			updateSidebarList(code, wlayer);
		}else{
			$("#list-accordion").hide();
		}

		$(".bread-link").on("click", function(){
			var $this = $(this);
			var code = $this.attr("code");
			var layer = $this.attr("layer");

			changeLayer(layer);
			updateSidebar(code, feature, layer);

			var feature_up = { properties: {} };
			var layers = ['pref', 'distlict', 'division'];
			for (var i in layers){
				var l = layers[i];
				if (feature.properties[l + 'Code']){
					feature_up.properties[l + 'Code'] = feature.properties[l + 'Code']; 
					feature_up.properties[l + 'Name'] = feature.properties[l + 'Name']; 
				}
				if (l == layer) break;
			}
			var code_prop = 'code';
			selected = { feature: feature_up, code: code, code_prop: code_prop };

			//map.on('data', function(){
			//	showArea(code);
			//	map.off('data');
			//});
		});
	}

	function setJMALink (code){
		if (show_layer == "pref"){
			$("#jma-link a").attr("href", "https://www.jma.go.jp/bosai/warning/#area_type=offices&area_code=" + code);
		}else if (show_layer == "city"){
			$("#jma-link a").attr("href", "https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code=" + code); 
		}else{
			$("#jma-link a").attr("href", "https://www.jma.go.jp/bosai/map.html?elem=all&contents=warning");
		}
	}

	function updateSidebarList (code, wlayer){
		var $list = $("#sidebar-list");
		var pcode = code.substr(0, 4) + "00";
		var dcode = code.substr(0, 5) + "0";
		var showdata, layer;

		// kagoshima
		if (pcode == "460000") {
			if (dcode != "460040"){
				pcode = "460100";
			}else{
				pcode = "460040";
			}
		}

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

		if (wlayer == "division"){
			if (citylist[pcode] && citylist[pcode].data[dcode] && citylist[pcode].data[dcode].data[code]){
				layer = "division";
				showdata = citylist[pcode].data[dcode].data[code].data;

			}else if (citylist[pcode] && citylist[pcode].data[pcode] && citylist[pcode].data[pcode].data[code]){
				layer = "division";
				showdata = citylist[pcode].data[pcode].data[code].data;

			}else if (citylist[dcode] && citylist[dcode].data[dcode] && citylist[dcode].data[dcode].data[code]){
				layer = "division";
				showdata = citylist[dcode].data[dcode].data[code].data;
			}
		}

		if (wlayer == "distlict"){
			if (citylist[pcode] && citylist[pcode].data[code]){
				layer = "distlict";
				showdata = citylist[pcode].data[code].data;

			}else if (citylist[dcode] && citylist[dcode].data[code]){
				layer = "distlict";
				showdata = citylist[dcode].data[code].data;
			}
		}

		if (!showdata){
			return console.error("not found");
		}

		for (var acode in showdata){
			var d = showdata[acode];
			$list.append('<div class="item"><a class="list-link" code=' + acode + '>' + d.name + '</a></div>');
		}

		$('#list-accordion .title').html('<i class="dropdown icon"></i>' + Object.keys(showdata).length + " 区域");
		if (mobile && layer == "division"){
			$("#list-accordion .title").removeClass("active");
			$("#list-accordion .content").removeClass("active");
		}else{
			$("#list-accordion .title").addClass("active");
			$("#list-accordion .content").addClass("active");
		}
		$('.ui.accordion').accordion();

		$(".list-link").on("click", function(){
			var code = $(this).attr("code");

			var down_layer = { pref: 'distlict', distlict: 'division', division: 'city' };
			var l = down_layer[layer];

			var feature_down = selected.feature;
			var code_prop = 'code';
			var name_prop = 'name';
			feature_down.properties[code_prop] = code;
			feature_down.properties[name_prop] = $(this).text();
			selected = { feature: feature_down, code: code, code_prop: code_prop };

			changeLayer(l);
			updateSidebar(code, feature_down, l);

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
