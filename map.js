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

	var layer = "city";
	var selected;

	map.on("load", function() {
		addVtileLayer(layer);

		map.on('mousemove', function(e) {
			var features = map.queryRenderedFeatures(e.point, { layers: ['warning-area-' + layer] });
			map.getCanvas().style.cursor = (features.length) ? 'crosshair' : '';

			if (!features.length) {
				popup.remove();
				return;
			}

			var feature = features[0];
			var name_prop = (layer == 'city') ? 'name' : layer + 'Name';

			popup.setLngLat(e.lngLat)
				.setText(feature.properties[name_prop])
				.addTo(map);
		});

		map.on('click', function(e) {
			var features = map.queryRenderedFeatures(e.point, { layers: ['warning-area-' + layer] });
			if (!features.length) return;

			map.getCanvas().style.cursor = 'pointer';
			var code_prop = (layer == 'city') ? 'code' : layer + 'Code';
			var code = features[0].properties[code_prop];
			map.setFilter("selected-area-" + layer, ["==", code_prop, code]);
			selected = { feature: features[0], code: code, code_prop: code_prop };
		});
	});

	$("#layer-select button").on("click", function (e){
		var $this = $(this);

		// .active
		if ($this.hasClass("active")) return;
		$("#layer-select .active").removeClass("active");
		$this.addClass("active");

		// change layer
		removeVtileLayer(layer);
		layer = $this.attr("l");
		addVtileLayer(layer);
	});

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
			if (selected.feature.properties[code_prop]){
				filter = ["==", code_prop, selected.feature.properties[code_prop]];
			}else{
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
});
