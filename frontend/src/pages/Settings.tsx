import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, Key } from 'lucide-react';
import { getUserSettings, updateUserSettings } from '../services/api';
import type { UserSettings } from '../types';

const Settings = () => {
  const [settings, setSettings] = useState<UserSettings>({
    theme: 'dark',
    notifications: true,
    api_keys: {},
  });
  const [saving, setSaving] = useState(false);
  const [showApiKeys, setShowApiKeys] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await getUserSettings();
      setSettings(data);
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateUserSettings(settings);
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-3xl mx-auto"
      >
        <h1 className="text-4xl font-bold gradient-text mb-8 text-center">Settings</h1>

        <div className="space-y-6">
          {/* General Settings */}
          <div className="glass-card p-6">
            <h2 className="text-2xl font-bold mb-6">General</h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">Theme</p>
                  <p className="text-sm text-gray-400">Choose your preferred theme</p>
                </div>
                <select
                  value={settings.theme}
                  onChange={(e) =>
                    setSettings({ ...settings, theme: e.target.value as any })
                  }
                  className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-purple-500 focus:outline-none"
                >
                  <option value="dark">Dark</option>
                  <option value="light">Light</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">Notifications</p>
                  <p className="text-sm text-gray-400">Receive analysis completion alerts</p>
                </div>
                <button
                  onClick={() =>
                    setSettings({ ...settings, notifications: !settings.notifications })
                  }
                  className={`w-12 h-6 rounded-full transition-all ${
                    settings.notifications ? 'bg-purple-600' : 'bg-gray-600'
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full transition-all ${
                      settings.notifications ? 'ml-6' : 'ml-1'
                    }`}
                  />
                </button>
              </div>

              <div>
                <label className="block font-semibold mb-2">Default Cancer Type</label>
                <select
                  value={settings.default_cancer_type || ''}
                  onChange={(e) =>
                    setSettings({ ...settings, default_cancer_type: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-purple-500 focus:outline-none"
                >
                  <option value="">None</option>
                  <option value="breast">Breast Cancer</option>
                  <option value="lung">Lung Cancer</option>
                  <option value="colorectal">Colorectal Cancer</option>
                  <option value="prostate">Prostate Cancer</option>
                  <option value="ovarian">Ovarian Cancer</option>
                  <option value="melanoma">Melanoma</option>
                  <option value="glioma">Glioma</option>
                  <option value="pancreatic">Pancreatic Cancer</option>
                  <option value="liver">Liver Cancer</option>
                  <option value="gastric">Gastric Cancer</option>
                </select>
              </div>
            </div>
          </div>

          {/* API Keys */}
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">API Keys</h2>
              <button
                onClick={() => setShowApiKeys(!showApiKeys)}
                className="text-sm text-purple-400 hover:text-purple-300"
              >
                {showApiKeys ? 'Hide' : 'Show'}
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block font-semibold mb-2 flex items-center gap-2">
                  <Key size={16} />
                  OpenAI API Key
                </label>
                <input
                  type={showApiKeys ? 'text' : 'password'}
                  value={settings.api_keys?.openai || ''}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      api_keys: { ...settings.api_keys, openai: e.target.value },
                    })
                  }
                  placeholder="sk-..."
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-purple-500 focus:outline-none font-mono text-sm"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Required for AI chat functionality
                </p>
              </div>

              <div>
                <label className="block font-semibold mb-2 flex items-center gap-2">
                  <Key size={16} />
                  Anthropic API Key
                </label>
                <input
                  type={showApiKeys ? 'text' : 'password'}
                  value={settings.api_keys?.anthropic || ''}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      api_keys: { ...settings.api_keys, anthropic: e.target.value },
                    })
                  }
                  placeholder="sk-ant-..."
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-purple-500 focus:outline-none font-mono text-sm"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Alternative AI provider for chat
                </p>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Save size={20} />
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default Settings;
