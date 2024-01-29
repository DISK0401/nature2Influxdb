curl --request GET \
  --url https://api.nature.global/1/appliances \
  --header 'Authorization: Bearer ${YOUR_NATURE_TOKEN}' \
  | jq '.[] | select(.id == ${NATURE_REMO_E_DEVICE_ID}").smart_meter.echonetlite_properties[] | {name: (.name), epc: (.epc), val: (.val|tonumber), updated_at: (.updated_at)}' \
  | jq -s
