# VMOS Cloud OpenAPI — endpoint index

Snapshot of https://cloud.vmoscloud.com/vmoscloud/doc/en/server/llms-ai-reference.txt (2026-10).
Full request/response schemas: https://cloud.vmoscloud.com/vmoscloud/doc/en/server/openapi.yaml
(fetch it and grep the path when you need exact params — it is ~240 KB, don't read it whole).

Auth: `scripts/vmos.py` already signs requests (V2: X-Access-Key / X-Timestamp / X-Sign =
sha256(SK + ts + path + body)). The upstream file's "x-date / HMAC authorization" section is the
legacy scheme — ignore it. Call any endpoint below with:

    vmos api <name> '<json>' [--with-pad] [--get]

`--with-pad` adds `"padCodes": [<default pad>]`. A few endpoints use `padCode` (singular) or
`padCodeList` instead — pass those in the JSON yourself.

## API List

## 1. Instance Management
POST  /vcpcloud/api/padApi/setWifiList - Modify instance WIFI properties
  Params: padCodes[], wifiJsonList[], SSID, BSSID, MAC, IP, gateway, DNS1, DNS2, hessid, anqpDomainId, capabilities, level, linkSpeed, txLinkSpeed, rxLinkSpeed, frequency, distance, distanceSd, channelWidth
POST  /vcpcloud/api/padApi/padDetails - Instance details
POST  /vcpcloud/api/padApi/restart - Instance restart
  Params: padCodes[]
POST  /vcpcloud/api/padApi/reset - Instance reset
  Params: padCodes[]
POST  /vcpcloud/api/padApi/padProperties - Query instance properties
  Params: padCode
POST  /vcpcloud/api/padApi/batchPadProperties - Batch query instance properties
  Params: padCodes[]
POST  /vcpcloud/api/padApi/updatePadProperties - Modify instance properties (dynamic)
  Params: padCodes[], modemPersistPropertiesList[], propertiesName, propertiesValue, modemPropertiesList[], systemPersistPropertiesList[], systemPropertiesList[], settingPropertiesList[], oaidPropertiesList[]
POST  /vcpcloud/api/padApi/updatePadAndroidProp - Modify instance Android modification props (restart required)
  Params: padCode, restart, props, ro.product.vendor.name
POST  /vcpcloud/api/padApi/updateSIM - Modify SIM by country code
  Params: padCode, countryCode, props, ro.product.vendor.name
POST  /vcpcloud/api/padApi/updateSIMByCountryAndPhone - Modify SIM by country and phone number
  Params: padCode, countryCode, phoneNumber
POST  /vcpcloud/api/padApi/dissolveRoom - Stop streaming
  Params: padCodes[]
POST  /vcpcloud/api/padApi/checkIP - Smart IP proxy detection
  Params: host, port, account, password, type, country, ip, loc, city, region, timezone
POST  /vcpcloud/api/padApi/smartIp - Set smart IP
  Params: padCodes[], host, port, account, password, type, mode, bypassPackageList[], bypassIpList[], bypassDomainList[], followLanguage
POST  /vcpcloud/api/padApi/notSmartIp - Cancel smart IP
  Params: padCodes[]
POST  /vcpcloud/api/padApi/getTaskStatus - Device task result query (smart IP)
  Params: taskId
POST  /vcpcloud/api/padApi/getListInstalledApp - Get installed apps for specified instances
  Params: padCodeList[]
POST  /vcpcloud/api/padApi/updateTimeZone - Modify instance timezone
  Params: timeZone, padCodes[]
POST  /vcpcloud/api/padApi/updateLanguage - Modify instance language
  Params: language, country, padCodes[]
POST  /vcpcloud/api/padApi/gpsInjectInfo - Set instance GPS
  Params: longitude, latitude, altitude, speed, bearing, horizontalAccuracyMeters, padCodes[]
POST  /vcpcloud/api/padApi/proxyInfo - Query instance proxy info
  Params: padCodes[], padCode
POST  /vcpcloud/api/padApi/replacePad - One-key new device
  Params: padCodes[], countryCode, realPhoneTemplateId, androidProp, replacementRealAdiFlag, excludeRealPhoneTemplateIds[], certificate, wipeData, wipeSpecificData[]
GET  /vcpcloud/api/padApi/country - Query one-key new device supported countries
  Params: None
POST  /vcpcloud/api/padApi/webview/version/list - Query available WebView versions
  Params: None
POST  /vcpcloud/api/padApi/updateContacts - Update contacts
  Params: padCodes[], fileUniqueId, operateType, info[], firstName, phone, email
POST  /vcpcloud/api/padApi/setProxy - Set instance proxy
  Params: account, password, ip, port, enable, padCodes[], proxyType, proxyName, model, bypassPackageList[], bypassIpList[], bypassDomainList[], limitPackageList[], limitIpList[], limitDomainList[], sUoT
POST  /vcpcloud/api/padApi/listInstalledApp - Real-time query installed app list
  Params: padCodes[], appName
POST  /vcpcloud/api/padApi/setKeepAliveApp - Set app keep-alive
  Params: padCodes[], applyAllInstances, appInfos[], serverName
POST  /vcpcloud/api/padApi/setHideAppList - Set app hide
  Params: padCodes[], appInfos[], packageName
POST  /vcpcloud/api/padApi/replaceRealAdiTemplate - Modify real device ADI template
  Params: padCodes[], wipeData, realPhoneTemplateId
POST  /vcpcloud/api/padApi/asyncCmd - Async execute ADB command
  Params: padCodes[], scriptContent
POST  /vcpcloud/api/padApi/enableSmsSendCallback - Enable outbound SMS callback
  Params: padCodes[]
POST  /vcpcloud/api/padApi/switchRoot - Switch Root permission
  Params: padCodes[], globalRoot, packageName, rootStatus
POST  /vcpcloud/api/padApi/screenshot - Local screenshot
  Params: padCodes[], rotation, broadcast, definition, resolutionHeight, resolutionWidth
POST  /vcpcloud/api/padApi/getLongGenerateUrl - Get instance real-time preview image
  Params: padCodes[], format, height, width, quality
POST  /vcpcloud/api/padApi/upgradeImage - Upgrade image
  Params: padCodes[], imageId, wipeData, enableCpuCoreConfig
POST  /vcpcloud/api/padApi/virtualRealSwitch - Upgrade real device image
  Params: padCodes[], imageId, wipeData, realPhoneTemplateId, upgradeImageConvertType, screenLayoutId, certificate, deviceAndroidProps, enableCpuCoreConfig
POST  /vcpcloud/api/padApi/userTemplateList - List personal uploaded templates
  Params: page, rows, id, templateId
POST  /vcpcloud/api/padApi/templateList - Paginated get real device templates
  Params: page, rows
POST  /vcpcloud/api/padApi/modelInfo - Batch get instance model info
  Params: padCodes[]
POST  /vcpcloud/api/padApi/openOnlineAdb - Enable/disable ADB
  Params: padCodes[], openStatus
POST  /vcpcloud/api/padApi/adb - Get ADB connection info
  Params: padCode, enable, expireMinutes
POST  /vcpcloud/api/padApi/batch/adb - Batch get ADB connection info
  Params: padCodes[], enable
POST  /vcpcloud/api/padApi/simulateTouch - Simulate touch
  Params: padCodes[], width, height, pointCount, positions[]
POST  /vcpcloud/api/padApi/padTaskDetail - Instance operation task details
  Params: taskIds[], taskId
POST  /vcpcloud/api/padApi/executeScriptInfo - Get instance script execution result
  Params: taskIds
POST  /vcpcloud/api/padApi/screenshotInfo - Get instance screenshot result
  Params: taskIds
POST  /vcpcloud/api/padApi/padExecuteTaskInfo - Instance restart/reset execution result
  Params: taskIds
POST  /vcpcloud/api/padApi/infos - Instance group list / instance list info
  Params: page, rows, padType, padCodes[]
POST  /vcpcloud/api/padApi/addPhoneRecord - Import call records
  Params: padCodes[], callRecords[]
POST  /vcpcloud/api/padApi/inputText - Cloud phone text input
  Params: padCodes[], text, code, msg, ts, data[], padCode, taskId, vmStatus, taskStatus
POST  /vcpcloud/api/padApi/simulateSendSms - Simulate send SMS
  Params: padCodes[], senderNumber, smsContent
POST  /vcpcloud/api/padApi/resetGAID - Reset GAID
  Params: padCodes[], resetGmsType, oprBy, taskSource
POST  /vcpcloud/api/padApi/injectAudioToMic - Inject audio to instance microphone
  Params: padCodes[], url, fileUniqueId, enable
POST  /vcpcloud/api/padApi/cleanAppHome - Clear processes and return to desktop
  Params: padCodes[]
POST  /vcpcloud/api/padApi/unmannedLive - Unmanned live streaming
  Params: padCodes[], injectSwitch, injectLoop, injectUrl, injectUrls[]
POST  /vcpcloud/api/padApi/injectPicture - Image injection
  Params: padCodes[], injectSwitch, injectLoop, injectUrl
POST  /vcpcloud/api/padApi/addUserRom - Upload user image
  Params: name, updateLog, androidVersion, version, downloadUrl, packageSize
POST  /vcpcloud/api/padApi/replacement - Device replacement
  Params: padCode
POST  /vcpcloud/api/padApi/confirmTransfer - Transfer cloud phone
  Params: padCodes[], makeOverMobilePhone
POST  /vcpcloud/api/padApi/setHideAccessibilityAppList - Hide accessibility service
  Params: padCodes[], appInfos[], packageName

## 2. Resource Management
POST  /vcpcloud/api/padApi/infos - Instance list info (paginated query ordered instances)
  Params: page, rows, padType, padCodes[]

## 3. Application Management
POST  /vcpcloud/api/padApi/uninstallApp - Uninstall app
  Params: apkPackageList[], padCodeList[]
POST  /vcpcloud/api/padApi/startApp - Start app
  Params: pkgName, padCodes[]
POST  /vcpcloud/api/padApi/stopApp - Stop app
  Params: pkgName, padCodes[]
POST  /vcpcloud/api/padApi/restartApp - Restart app
  Params: pkgName, padCodes[]
POST  /vcpcloud/api/padApi/listInstalledApp - Instance installed app list query
  Params: padCodes[], appName
POST  /vcpcloud/api/padApi/uploadFileV3 - Upload file via URL
  Params: padCodes[], padCode, autoInstall, fileUniqueId, customizeFilePath, fileName, packageName, url, md5, isAuthorization, iconPath
POST  /vcpcloud/api/padApi/uploadFile - Upload file to cloud storage
  Params: file
POST  /vcpcloud/api/padApi/deleteOssFiles - Delete cloud storage files
  Params: files[], urls[]
POST  /vcpcloud/api/padApi/selectFiles - Query user file list
  Params: None

## 4. Task Management
POST  /vcpcloud/api/padApi/padTaskDetail - Instance operation task details
  Params: taskIds[], taskId
POST  /vcpcloud/api/padApi/fileTaskDetail - File task details
  Params: taskIds[], taskId

## 5. Cloud Phone Management
POST  /vcpcloud/api/padApi/createMoneyOrder - Create/renew cloud phone
  Params: androidVersionName, goodId, goodNum, autoRenew, equipmentId, countryCode, imageId
POST  /vcpcloud/api/padApi/selectPaidOrderList - Query paid orders (bill export)
  Params: orderId, businessType, completeStartTime, completeEndTime, page, rows
POST  /vcpcloud/api/padApi/userPadList - Cloud phone list
  Params: padCode, equipmentIds[]
POST  /vcpcloud/api/padApi/padInfo - Cloud phone info query
  Params: padCode
GET  /vcpcloud/api/padApi/getCloudGoodList - SKU package list
  Params: androidVersion, goodIds
POST  /vcpcloud/api/padApi/createMoneyProOrder - Device presale purchase
  Params: androidVersionName, goodId, goodNum, autoRenew, countryCode
POST  /vcpcloud/api/padApi/queryProOrderList - Query presale order result details
  Params: proBuyStatus, orderId
POST  /vcpcloud/api/padApi/imageVersionList - Android image version list
  Params: padCode
GET  /vcpcloud/api/padApi/timingDeviceModels - List timing device models
  Params: androidVersion
POST  /vcpcloud/api/padApi/createByTimingOrder - Create timing device order
  Params: goodId, goodTimeId, goodNum, androidVersion, deviceModelId
POST  /vcpcloud/api/padApi/timingPadOn - Timing device power on
  Params: padCodes[], defCode, netStorageResUnitCode
POST  /vcpcloud/api/padApi/timingPadOff - Timing device power off
  Params: padCodes[], isBackUp
POST  /vcpcloud/api/padApi/timingPadPowerLogList - List timing device power logs
  Params: padCode, page, size
POST  /vcpcloud/api/padApi/timingPadDel - Timing device destroy
  Params: padCodes[]
GET  /vcpcloud/api/padApi/vcTimingBackupList - Storage resource package list
  Params: None
GET  /vcpcloud/api/padApi/getRenewStorageInfo - Cloud storage remaining capacity
  Params: None
GET  /vcpcloud/api/padApi/getVcStorageGoods - Cloud storage product list
  Params: None
POST  /vcpcloud/api/padApi/buyStorageGoods - Purchase cloud storage expansion
  Params: storageId, autoRenewOrder
GET  /vcpcloud/api/padApi/selectAutoRenew - Cloud storage renewal details query
  Params: None
POST  /vcpcloud/api/padApi/renewsStorageGoods - Aggregate renew cloud storage products
  Params: autoRenewOrder
GET  /vcpcloud/api/padApi/updateRenewStorageStatus - Cloud storage auto-renewal switch
  Params: renewStorageStatus
POST  /vcpcloud/api/padApi/listPadBackupIds - List available cloud backup IDs
  Params: None
POST  /vcpcloud/api/padApi/listPadBackups - List available cloud backup details
  Params: name (optional)
POST  /vcpcloud/api/padApi/backupCalculate - Calculate cloud backup size
  Params: padCode
POST  /vcpcloud/api/padApi/queryBackupCalculateResult - Query cloud backup size
  Params: padCode
POST  /vcpcloud/api/padApi/addBackup - Create cloud backups
  Params: vcPadBackupList[]
POST  /vcpcloud/api/padApi/queryBackupBatch - Query cloud backup progress
  Params: batchId
POST  /vcpcloud/api/padApi/clonePadBackup - Clone from cloud backup
  Params: vcPadBackupList[], pads[]
POST  /vcpcloud/api/padApi/deleteUploadFiles - Delete backup resource package data
  Params: backupIds[]
POST  /vcpcloud/api/padApi/toggleProcessHide - Show or hide app process
  Params: padCodes[], show, packageName

## 6. Email Verification Service
GET  /vcpcloud/api/padApi/getEmailServiceList - Get email service list
  Params: None
GET  /vcpcloud/api/padApi/getEmailTypeList - Get email type and remaining stock
  Params: serviceId
POST  /vcpcloud/api/padApi/createEmailOrder - Create email order
  Params: serviceId, emailTypeId, goodNum
GET  /vcpcloud/api/padApi/getEmailOrder - Query purchased email list
  Params: page, size, serviceId, email, status
GET  /vcpcloud/api/padApi/getEmailCode - Refresh get email verification code
  Params: orderId

## 7. Dynamic Proxy Service
GET  /vcpcloud/api/padApi/getDynamicGoodService - Query dynamic proxy product list
  Params: None
GET  /vcpcloud/api/padApi/getDynamicProxyRegion - Query dynamic proxy region list
  Params: None
GET  /vcpcloud/api/padApi/queryCurrentTrafficBalance - Get dynamic proxy current balance
  Params: None
GET  /vcpcloud/api/padApi/getDynamicProxyHost - Query supported server regions
  Params: None
POST  /vcpcloud/api/padApi/buyDynamicProxy - Purchase dynamic proxy traffic package
  Params: goodId, goodNum, autoRenewOrder
POST  /vcpcloud/api/padApi/createProxy - Create dynamic proxy
  Params: city, countryCode, goodNum, proxyHost, proxyType, proxyUseType, state, time
GET  /vcpcloud/api/padApi/getProxys - Query dynamic proxy list
  Params: page, rows
POST  /vcpcloud/api/padApi/getDynamicProxyOrders - Query dynamic proxy order list
  Params: page, rows, completeStartTime, completeEndTime
POST  /vcpcloud/api/padApi/batchPadConfigProxy - Configure dynamic proxy for instances
  Params: padCodes[], setProxyFlag, proxyIds[]
POST  /vcpcloud/api/padApi/selectBatchPadProxyTask - Query batch instance set proxy task
  Params: taskId
GET  /vcpcloud/api/padApi/getDynamicProxyAutomaticRenewal - Query dynamic proxy auto-renewal info
  Params: None
POST  /vcpcloud/api/padApi/setAutoRenewSwitch - Set dynamic proxy auto-renewal switch
  Params: autoRenewOrder
POST  /vcpcloud/api/padApi/delProxyByIds - Delete dynamic proxy
  Params: ids[]

## 8. Static Residential Proxy Service
GET  /vcpcloud/api/padApi/proxyGoodList - Get static residential product list
  Params: None
GET  /vcpcloud/api/padApi/getProxyRegion - Get static residential supported countries/cities
  Params: None
POST  /vcpcloud/api/padApi/createProxyOrder - Static residential product purchase
  Params: proxyGoodId, region, num, country, proxyAddress, autoRenew, clientRequestId
POST  /vcpcloud/api/padApi/selectProxyOrderList - Static residential proxy order details
  Params: page, rows
POST  /vcpcloud/api/padApi/createRenewProxyOrder - Static residential proxy renewal
  Params: proxyGoodId, proxyIps, autoRenew
POST  /vcpcloud/api/padApi/queryProxyList - Query static residential proxy list
  Params: current, size

## 9. Real Device Testing
GET  /vcpcloud/api/padApi/realMachineTrialAvailability - List available real-device test models
  Params: None
POST  /vcpcloud/api/padApi/createRealMachineTrial - Create a real-device test device
  Params: templateId
GET  /vcpcloud/api/padApi/realMachineTrialGoods - List real-device test time products
  Params: None
POST  /vcpcloud/api/padApi/buyRealMachineTrialTime - Purchase real-device test time
  Params: goodId, quantity, requestId

## 10. SDK Token
POST  /vcpcloud/api/padApi/stsTokenByPadCode - Get SDK temporary token by padCode
  Params: padCode
GET  /vcpcloud/api/padApi/getSessionToken - Get group control session token
POST  /vcpcloud/api/padApi/clearStsToken - Clear SDK authorization token
  Params: token

## 11. Cloud Number Service
POST  /vcpcloud/api/padApi/cloudNumber/skus - Query cloud number plans and inventory
  Params: areaCode
POST  /vcpcloud/api/padApi/cloudNumber/purchase - Purchase cloud number
  Params: countryCode, areaCode, planId, quantity, autoRenew, clientToken, expectedTotalCents
POST  /vcpcloud/api/padApi/cloudNumber/purchase/status - Query purchase result
  Params: clientToken
POST  /vcpcloud/api/padApi/cloudNumber/list - Query cloud number list
  Params: countryCode, status, keyword, page, size
POST  /vcpcloud/api/padApi/cloudNumber/autoRenew - Update cloud number auto renewal
  Params: id, autoRenew, rowVersion
POST  /vcpcloud/api/padApi/cloudNumber/release - Release cloud number
  Params: number
POST  /vcpcloud/api/padApi/cloudNumber/sms/list - Query cloud number SMS
  Params: number, keyword, page, size
POST  /vcpcloud/api/padApi/cloudNumber/bind - Start cloud phone binding
  Params: numberId, padCode, requestId, restartAcknowledged
POST  /vcpcloud/api/padApi/cloudNumber/bind/status - Query cloud phone binding status
  Params: numberId

## 12. Social Account Service
POST  /vcpcloud/api/padApi/socialAccount/listings - Query social account listings
  Params: categoryId, subcategoryId, search, sort, direction, page, perPage
POST  /vcpcloud/api/padApi/socialAccount/purchase - Purchase social accounts
  Params: requestNo, listingId, listingSlug, listingTitle, quantity, expectedUnitPrice
POST  /vcpcloud/api/padApi/socialAccount/purchase/status - Query social account purchase result
  Params: requestNo
POST  /vcpcloud/api/padApi/socialAccount/orders - Query social account orders
  Params: page, size
POST  /vcpcloud/api/padApi/socialAccount/order/detail - Query social account order details
  Params: orderNo

## Callback Events

69 - SMS sending event (eventType)
999 - Instance status callback
1000 - Instance restart task
1001 - Instance reset task
1002 - Async ADB task
1003 - App install task
1004 - App uninstall task
1005 - App stop task
1006 - App restart task
1007 - App start task
1009 - Instance file upload task
1012 - Instance upgrade image task
1124 - One-key new device
4001 - User image upload

Details and examples see callback.md

## Common Error Codes

200 - Success
2031 - Invalid key
2032 - Missing Authorization header
2019 - Signature verification failed
100000 - Invalid request parameters
100003 - Missing Authorization header
100004 - Invalid signature
100005 - Signature verification failed
110028 - Instance not found
110013 - Instance not found
110031 - Instance not ready
120008 - Token not owned by current user

More error codes see ErrorCode.md

