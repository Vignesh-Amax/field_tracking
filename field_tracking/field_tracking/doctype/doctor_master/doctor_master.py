# Copyright (c) 2025, Tirthan Shah and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document

class DoctorMaster(Document):
    def validate(self):
        if self.address and not (self.pincode and self.latitude and self.longitude):
            self.auto_populate_address_fields()

    def auto_populate_address_fields(self):
        api_key = frappe.conf.get("google_maps_api_key")
        if not api_key:
            frappe.msgprint("Google Maps API key not configured", alert=True)
            return

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": self.address,
            "key": api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("status") == "OK" and data.get("results"):
                result = data["results"][0]

                # Extract pincode
                for comp in result.get("address_components", []):
                    if "postal_code" in comp.get("types", []):
                        self.pincode = comp.get("long_name")
                        break

                # Extract lat/lng
                loc = result.get("geometry", {}).get("location", {})
                self.latitude = str(loc.get("lat", ""))
                self.longitude = str(loc.get("lng", ""))

        except Exception as e:
            frappe.log_error(f"Geocoding failed for {self.name}: {str(e)}")
            frappe.msgprint("Failed to auto-fill address details", alert=True)
