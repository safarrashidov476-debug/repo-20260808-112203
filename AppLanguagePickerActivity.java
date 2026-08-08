package com.github.olga_yakovleva.rhvoice.android;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.SparseBooleanArray;
import android.view.ViewGroup;
import android.widget.AbsListView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.Toast;

import androidx.preference.PreferenceManager;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class AppLanguagePickerActivity extends Activity {

    private static final String PREF_KEY = "custom_app_language_map";

    private List<String> labels;
    private List<String> packages;
    private ListView listView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        showLanguageDialog();
    }

    private void showLanguageDialog() {
        final String[] items = {"O'zbek", "Rus"};
        final String[] codes = {"uzb", "rus"};
        new AlertDialog.Builder(this)
                .setTitle("Tilni tanlang")
                .setItems(items, (dialog, which) -> showAppListScreen(codes[which], items[which]))
                .setOnCancelListener(dialog -> finish())
                .show();
    }

    private void showAppListScreen(final String langCode, String langLabel) {
        loadInstalledApps();

        Map<String, String> currentMap = parseMap(
                PreferenceManager.getDefaultSharedPreferences(this).getString(PREF_KEY, ""));

        listView = new ListView(this);
        listView.setChoiceMode(AbsListView.CHOICE_MODE_MULTIPLE);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(
                this, android.R.layout.simple_list_item_multiple_choice, labels);
        listView.setAdapter(adapter);

        for (int i = 0; i < packages.size(); i++) {
            if (langCode.equals(currentMap.get(packages.get(i)))) {
                listView.setItemChecked(i, true);
            }
        }

        Button saveButton = new Button(this);
        saveButton.setText("Saqlash");
        saveButton.setOnClickListener(v -> {
            saveSelection(langCode);
            Toast.makeText(this, "Saqlandi", Toast.LENGTH_SHORT).show();
            finish();
        });

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.addView(listView, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));
        root.addView(saveButton, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        setTitle(langLabel);
        setContentView(root);
    }

    private void loadInstalledApps() {
        PackageManager pm = getPackageManager();
        List<ApplicationInfo> installed = pm.getInstalledApplications(PackageManager.GET_META_DATA);

        final List<ApplicationInfo> filtered = new ArrayList<>();
        for (ApplicationInfo ai : installed) {
            boolean isSystem = (ai.flags & ApplicationInfo.FLAG_SYSTEM) != 0;
            if (isSystem)
                continue;
            if (getPackageName().equals(ai.packageName))
                continue;
            filtered.add(ai);
        }

        Collections.sort(filtered, new Comparator<ApplicationInfo>() {
            @Override
            public int compare(ApplicationInfo a, ApplicationInfo b) {
                return String.valueOf(pmLabel(a)).compareToIgnoreCase(String.valueOf(pmLabel(b)));
            }
        });

        labels = new ArrayList<>();
        packages = new ArrayList<>();
        for (ApplicationInfo ai : filtered) {
            labels.add(pmLabel(ai) + "\n" + ai.packageName);
            packages.add(ai.packageName);
        }
    }

    private CharSequence pmLabel(ApplicationInfo ai) {
        return getPackageManager().getApplicationLabel(ai);
    }

    private void saveSelection(String langCode) {
        SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(this);
        Map<String, String> map = parseMap(prefs.getString(PREF_KEY, ""));

        SparseBooleanArray checked = listView.getCheckedItemPositions();
        for (int i = 0; i < packages.size(); i++) {
            String pkg = packages.get(i);
            boolean isChecked = checked.get(i);
            if (isChecked) {
                map.put(pkg, langCode);
            } else if (langCode.equals(map.get(pkg))) {
                map.remove(pkg);
            }
        }

        prefs.edit().putString(PREF_KEY, serializeMap(map)).apply();
    }

    private static Map<String, String> parseMap(String raw) {
        Map<String, String> map = new LinkedHashMap<>();
        if (raw == null || raw.trim().isEmpty())
            return map;
        for (String entry : raw.split(";")) {
            entry = entry.trim();
            int eq = entry.indexOf('=');
            if (eq <= 0)
                continue;
            String pkg = entry.substring(0, eq).trim();
            String code = entry.substring(eq + 1).trim();
            if (!pkg.isEmpty() && !code.isEmpty())
                map.put(pkg, code);
        }
        return map;
    }

    private static String serializeMap(Map<String, String> map) {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> e : map.entrySet()) {
            if (sb.length() > 0)
                sb.append(';');
            sb.append(e.getKey()).append('=').append(e.getValue());
        }
        return sb.toString();
    }
}
