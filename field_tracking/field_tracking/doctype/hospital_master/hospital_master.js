// Copyright (c) 2025, Tirthan Shah and contributors
// For license information, please see license.txt

// Copyright (c) 2025, Tirthan Shah and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hospital Master", {
    address: function(frm) {
        if (frm.doc.address) {
            // Debounce to avoid too many API calls while typing
            if (frm.address_geocode_timeout) {
                clearTimeout(frm.address_geocode_timeout);
            }
            frm.address_geocode_timeout = setTimeout(() => {
                geocode_address(frm);
            }, 1000); // Wait 1 second after user stops typing
        }
    }
});

async function geocode_address(frm) {
    const address = frm.doc.address.trim();
    if (!address) return;

    const api_key = "AIzaSyAgi3VBhF9IHrsLO9bAp1c0P-4Oan2hh94";
    const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${api_key}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.status === "OK" && data.results.length > 0) {
            const result = data.results[0];
            let pincode = null;
            let lat = null;
            let lng = null;

            // Extract pincode (postal_code)
            for (const component of result.address_components) {
                if (component.types.includes("postal_code")) {
                    const pc = parseInt(component.long_name);
                    if (!isNaN(pc)) pincode = pc;
                    break;
                }
            }

            // Extract lat/lng
            if (result.geometry?.location) {
                lat = parseFloat(result.geometry.location.lat);
                lng = parseFloat(result.geometry.location.lng);
            }

            // Only update if values are valid and different
            let update_obj = {};
            let update_needed = false;

            if (pincode !== null && frm.doc.pincode !== pincode) {
                update_obj.pincode = pincode;
                update_needed = true;
            }
            if (lat !== null && frm.doc.latitude !== lat) {
                update_obj.latitude = lat;
                update_needed = true;
            }
            if (lng !== null && frm.doc.longitude !== lng) {
                update_obj.longitude = lng;
                update_needed = true;
            }

            if (update_needed) {
                frm.set_value(update_obj);
                frappe.show_alert({
                    message: __("Address geocoded successfully"),
                    indicator: "green"
                });
            }
        } else {
            console.warn("Geocoding failed:", data.status);
            frappe.show_alert({
                message: __("Could not geocode address"),
                indicator: "orange"
            });
        }
    } catch (error) {
        console.error("Geocoding error:", error);
        frappe.show_alert({
            message: __("Geocoding failed due to network error"),
            indicator: "red"
        });
    }
}
