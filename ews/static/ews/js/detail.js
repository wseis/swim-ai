var geojsonMarkerOptions = {
    radius: 8,
    fillColor: "rgb(0, 86, 110)",
    color: "grey",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
};

var styleByType = {
    Network: {
        color: 'rgb(255, 130, 104)',
        radius: 4
    },
    Rainfall: {
        color: 'rgb(117, 195, 255)'
        //, radius: ?
    },
    WWTP: {
        color: 'rgb(178, 83, 64)',
        radius: 12
    },
    Riverflow: {
        color: 'rgb(64, 129, 178)',
        radius: 10
    },
    BathingSpot: {
        color: '#3185ff',
        radius: 10
    },
    other: {
        color: 'red'
        //, radius: ?
    }
};

function getStyle(type) {
    var style = styleByType[type];
    return (style === undefined ? styleByType['other'] : style);
}

function getColor(type) {
    var color = getStyle(type)['color'];
    return (color === undefined ? getStyle('other')['color'] : color);
}

// This function may return undefined
function getRadius(type) {
    var radius = getStyle(type)['radius'];
    return (radius === undefined ? getStyle('other')['radius'] : radius);
}

function getFillColorAndColorByType(type) {

    // Initialise result object with fillColor attribute
    var color = getColor(type);
    var result = {fillColor: color};

    // For WWTP and BathingSpot, set also the color attribute
    if (! (type == 'BathingSpot' )) {//|| type == 'BathingSpot')) {
        result['color'] = color;
    }
    
    return result;
}

function getFillColorAndRadiusByType(type) {

    // Initialise result object with fillColor attribute
    var result = {fillColor: getColor(type)};
    
    // If radius is defined for the type, add the radius attribute
    var radius = getRadius(type);
    if (radius !== undefined) {
        result['radius'] = radius;
    }
    
    return result;
}

// This function requires global variables/functions:
// - L (seems to be provided by "{% leaflet_js plugins="forms" %}" in templates)
// - collection
// - areas
function map_init(map, options) {
    var layerControl = L.control.layers().addTo(map);
    var sites = L.geoJson(collection, {
        onEachFeature: function (feature, layer) {
            if (feature.properties && feature.properties.popupContent) {
                layer.bindPopup(feature.properties.popupContent);
            }
        },
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, geojsonMarkerOptions);
        },
        style: function(feature) {
            return getFillColorAndRadiusByType(feature.properties.SiteType);
        }
    })
    
    layerControl.addOverlay(sites, "Sites");
    sites.addTo(map)

    var area_layer = L.geoJson(areas, {
        style: function(feature) {
            return getFillColorAndColorByType(feature.properties.SiteType);
        }
    })

    // Used only in model_fit.html
    layerControl.addOverlay(area_layer, "SelectAreas");
    area_layer.addTo(map)

    var legend = L.control({position: 'bottomright'});
    legend.onAdd = function (map) {
        
        var div = L.DomUtil.create('div', 'info legend'),
        grades = ['Network', 'Rainfall', 'WWTP', 'BathingSpot', 'Riverflow'],
        labels = [];
        
        // loop through our density intervals and generate a label with a colored square for each interval
        for (var i = 0; i < grades.length; i++) {
            div.innerHTML += '<i style="background:' + getColor(grades[i]) + '"></i> ';
            div.innerHTML += '<span>' + grades[i] + '</span>';
            div.innerHTML += '<br>';
            //div.innerHTML += (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
        }    
        
        return div;
    };
    
    legend.addTo(map);

    // Used only in detail.html
    var coords = collection.features[0].geometry.coordinates
    map.setView([coords[1], coords[0]], 13);
}
