# -*- coding: utf-8 -*-
#
# JSON data to be used with model mommey
#
EIGHTYTHREEB_DATA = {
  "transfer_value_share": "20.0",
  "tracking_code": "70132630000013657033",
  "nature_of_restrictions": "test",
  "date_of_property_transfer": "2013-12-20",
  "city": "Mönchengladbach",
  "details_confirmed": True,
  "markers": {
    "lawyer_complete_form": {
      "actor_name": "",
      "date_of": "2013-12-23T11:46:48"
    }
  },
  "tax_year": 2013,
  "state": "CA",
  "company_name": "LawPal (test)",
  "post_code": "90210",
  "description": "test",
  "address1": "Sophienstraße 37a-39",
  "address2": "",
  "transfer_value_total": "20.0",
  "client_full_name": "Test User",
  "ssn": "687-65-4329",
  "has_spouse": True,
  "disclaimer_agreed": True,
  "itin": "",
  "accountant_email": "test+accountant@lawpal.com",
  "client_email": "test+customer@lawpal.com"
}

EIGHTYTHREEB_TRACKINGCODE_DATA = EIGHTYTHREEB_DATA.copy()
# Has no mail_to_irs_tracking_code entry
if 'mail_to_irs_tracking_code' in EIGHTYTHREEB_TRACKINGCODE_DATA['markers']:
    del EIGHTYTHREEB_TRACKINGCODE_DATA['markers']['mail_to_irs_tracking_code']
