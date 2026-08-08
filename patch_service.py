import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """applyMappedSettings(tts);
            final SynthesisParameters params = new SynthesisParameters();
            params.setVoiceProfile(profileSpec);
            params.setRate(((double) rate) / 100.0);
            params.setPitch(((double) pitch) / 100.0);
            final Player player = new Player(callback);
            tts.engine.speak(request.getText(), params, player);
            player.setSampleRate(24000);
            callback.done();"""

new_block = """applyMappedSettings(tts);
            String processedText = PhoneNumberPreprocessor.process(request.getText());
            final Player player = new Player(callback);

            SharedPreferences customPrefs = PreferenceManager.getDefaultSharedPreferences(this);

            String appVoiceName = null;
            String appMapRaw = customPrefs.getString("custom_app_language_map", "");
            if (appMapRaw != null && !appMapRaw.trim().isEmpty()) {
                String foregroundPkg = null;
                android.app.usage.UsageStatsManager usm =
                        (android.app.usage.UsageStatsManager) getSystemService(android.content.Context.USAGE_STATS_SERVICE);
                if (usm != null) {
                    long end = System.currentTimeMillis();
                    long begin = end - 10000;
                    android.app.usage.UsageEvents events = usm.queryEvents(begin, end);
                    if (events != null) {
                        android.app.usage.UsageEvents.Event event = new android.app.usage.UsageEvents.Event();
                        while (events.hasNextEvent()) {
                            events.getNextEvent(event);
                            if (event.getEventType() == android.app.usage.UsageEvents.Event.MOVE_TO_FOREGROUND) {
                                foregroundPkg = event.getPackageName();
                            }
                        }
                    }
                }
                if (foregroundPkg != null) {
                    for (String entry : appMapRaw.split(";")) {
                        entry = entry.trim();
                        int eq = entry.indexOf('=');
                        if (eq <= 0)
                            continue;
                        String linePkg = entry.substring(0, eq).trim();
                        String voiceSpec = entry.substring(eq + 1).trim();
                        if (!linePkg.equals(foregroundPkg) || voiceSpec.isEmpty())
                            continue;
                        for (AndroidVoiceInfo v : tts.voices) {
                            if (voiceSpec.equals(v.getSource().getName())) {
                                appVoiceName = voiceSpec;
                                break;
                            }
                        }
                        if (appVoiceName == null) {
                            for (AndroidVoiceInfo v : tts.voices) {
                                if (voiceSpec.equals(v.getSource().getLanguage().getAlpha3Code())) {
                                    appVoiceName = v.getSource().getName();
                                    break;
                                }
                            }
                        }
                        break;
                    }
                }
            }

            boolean cyrillicToRussianEnabled = customPrefs.getBoolean("custom_cyrillic_to_russian", false);

            AndroidVoiceInfo russianVoice = null;
            if (cyrillicToRussianEnabled && !"rus".equals(bestMatch.voice.getLanguage())) {
                for (AndroidVoiceInfo v : tts.voices) {
                    if ("rus".equals(v.getSource().getLanguage().getAlpha3Code())) {
                        russianVoice = v;
                        break;
                    }
                }
            }

            if (appVoiceName != null) {
                SynthesisParameters params = new SynthesisParameters();
                params.setVoiceProfile(appVoiceName);
                params.setRate(((double) rate) / 100.0);
                params.setPitch(((double) pitch) / 100.0);
                tts.engine.speak(processedText, params, player);
            } else if (russianVoice != null) {
                String primaryVoiceName = bestMatch.voice.getSource().getName();
                String russianVoiceName = russianVoice.getSource().getName();
                java.util.List<String> segments = new java.util.ArrayList<>();
                java.util.List<Boolean> isCyrillicSeg = new java.util.ArrayList<>();
                splitByScript(processedText, segments, isCyrillicSeg);

                for (int i = 0; i < segments.size(); i++) {
                    String seg = segments.get(i);
                    if (seg.isEmpty())
                        continue;
                    SynthesisParameters segParams = new SynthesisParameters();
                    segParams.setVoiceProfile(isCyrillicSeg.get(i) ? russianVoiceName : primaryVoiceName);
                    segParams.setRate(((double) rate) / 100.0);
                    segParams.setPitch(((double) pitch) / 100.0);
                    tts.engine.speak(seg, segParams, player);
                }
            } else {
                final SynthesisParameters params = new SynthesisParameters();
                params.setVoiceProfile(profileSpec);
                params.setRate(((double) rate) / 100.0);
                params.setPitch(((double) pitch) / 100.0);
                tts.engine.speak(processedText, params, player);
            }

            player.setSampleRate(24000);
            callback.done();"""

if old_block not in content:
    print("XATO: eski blok topilmadi - RHVoice manbasi o'zgargan bo'lishi mumkin")
    sys.exit(1)

content = content.replace(old_block, new_block, 1)

helper_method = """
    private static void splitByScript(String text, java.util.List<String> segments, java.util.List<Boolean> isCyrillic) {
        if (text.isEmpty()) {
            segments.add(text);
            isCyrillic.add(false);
            return;
        }
        int n = text.length();
        int segStart = 0;
        boolean currentIsCyr = false;
        boolean typeSet = false;
        for (int i = 0; i < n; i++) {
            char c = text.charAt(i);
            if (!Character.isLetter(c))
                continue;
            boolean cyr = (c >= '\\u0400' && c <= '\\u04FF');
            if (!typeSet) {
                currentIsCyr = cyr;
                typeSet = true;
                continue;
            }
            if (cyr != currentIsCyr) {
                segments.add(text.substring(segStart, i));
                isCyrillic.add(currentIsCyr);
                segStart = i;
                currentIsCyr = cyr;
            }
        }
        segments.add(text.substring(segStart));
        isCyrillic.add(currentIsCyr);
    }

    @Override
    public String onGetDefaultVoiceNameFor(String language, String country, String variant) {"""

anchor = """    @Override
    public String onGetDefaultVoiceNameFor(String language, String country, String variant) {"""

if anchor not in content:
    print("XATO: onGetDefaultVoiceNameFor ankeri topilmadi")
    sys.exit(1)

content = content.replace(anchor, helper_method, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("RHVoiceService.java muvaffaqiyatli patch qilindi")
