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

	var layer = "distlict";
	var selected_code = "";

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

			popup.setLngLat(e.lngLat)
				.setText(feature.properties.name)
				.addTo(map);
		});
	});

	function addVtileLayer (layer){
		var source_layer = ((layer == 'city') ? '' : layer) + 'allgeojson';
		var source_suffix = (layer == 'city') ? '' : '-' + layer;

		map.addSource("vtile-" + layer, {
			"type": "vector",
			"minzoom": 0,
			"maxzoom": 10,
			"tiles": ["https://s3-ap-northeast-1.amazonaws.com/vector-tile/warning-area" + source_suffix + "/{z}/{x}/{y}.pbf"]
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

		map.addLayer({
			"id": "selected-area-" + layer,
			"type": "fill",
			"source": "vtile-" + layer,
			"source-layer": source_layer,
			"paint": {
				"fill-color": "rgba(245, 143, 152, 0.4)",
				"fill-outline-color": "rgba(245, 143, 152, 0.7)"
			},
			"filter": ["==", "code", ""]
		});

		map.on('click', 'warning-area-' + layer, select);
		map.on('touchend', 'warning-area-' + layer, select);

		function select (e) {
			map.getCanvas().style.cursor = 'pointer';
			console.log(e);

			var code = e.features[0].properties.code;
			map.setFilter("selected-area-" + layer, ["==", "code", code]);
		}
	}
});
