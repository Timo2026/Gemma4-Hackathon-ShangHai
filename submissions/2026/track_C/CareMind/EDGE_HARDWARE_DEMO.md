# Edge Hardware Demo Guide

This guide is for the Track C hardware video.

## Goal

Show that CareMind can handle a sensitive dementia-care note on an Android phone using Privacy Mode and a downloaded Gemma LiteRT model.

## Recommended Script

1. Show the Android phone with CareMind installed.
2. Open Settings / Privacy Mode.
3. Show the model list loaded from the backend.
4. Show the downloaded model status.
5. Turn off network.
6. Enter:

```text
外婆夜里醒了四次，一直说有人偷钱，晚饭只吃了几口，妈妈也很累。
```

7. Tap the local organize / generate action.
8. Show non-diagnostic output:

```text
观察到：夜间醒来、少食、被害感表达、照护者疲惫。
今晚先做一件小事：确认门锁和走廊夜灯。
沟通建议：你是不是很担心？我陪你一起找找。
边界：这不是诊断、处方或检查判断。
```

## Video Caption

```text
Network off. Gemma LiteRT runs on the Android device for local care-note understanding.
```

## APK Notes

The APK should be built with a deployed backend URL:

```bash
cd frontend/android
NODE_ENV=production \
EXPO_PUBLIC_CAREMIND_API_URL=https://caremind-1039168666325.us-west1.run.app \
./gradlew :app:assembleRelease
```

The model file is downloaded after installation, not bundled into the APK.

## Model Hosting

Upload LiteRT model files to the backend bucket:

```bash
gcloud storage cp ./Gemma3-1B-IT_multi-prefill-seq_q4_ekv4096.litertlm gs://caremind-498713-models-asia/models/
```

The APK reads the catalog dynamically:

```http
GET https://caremind-1039168666325.us-west1.run.app/api/models
```
