
import React from 'react';
import { ApiResponseData } from '../types';
import { Copy, Download, Terminal, Clock, AlertCircle, CheckCircle2 } from 'lucide-react';

interface ResponsePanelProps {
  response: ApiResponseData | null;
}

export const ResponsePanel: React.FC<ResponsePanelProps> = ({ response }) => {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const downloadJson = () => {
    if (!response) return;
    const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agroarc-response-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!response) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 flex flex-col items-center justify-center text-slate-400 h-full min-h-[400px]">
        <Terminal className="w-12 h-12 mb-4 opacity-20" />
        <p className="text-sm font-medium">Waiting for API Request...</p>
      </div>
    );
  }

  const isError = response.status === 0 || response.status >= 400;

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden flex flex-col h-full sticky top-6">
      <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isError ? (
            <AlertCircle className="w-5 h-5 text-red-500" />
          ) : (
            <CheckCircle2 className="w-5 h-5 text-emerald-500" />
          )}
          <span className="font-semibold text-slate-700">API Response Panel</span>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={downloadJson}
            className="p-2 hover:bg-white rounded-lg transition-colors border border-transparent hover:border-slate-200"
            title="Download JSON"
          >
            <Download className="w-4 h-4 text-slate-600" />
          </button>
        </div>
      </div>

      <div className="p-4 bg-slate-900 text-slate-300 flex items-center justify-between text-xs font-mono">
        <div className="flex gap-4">
          <span>Status: <span className={isError ? "text-red-400" : "text-emerald-400"}>{response.status || 'ERROR'}</span></span>
          <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {response.timestamp}</span>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-6">
        {response.error && (
          <div className="bg-red-50 border border-red-100 p-3 rounded-lg flex gap-3 text-red-700 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p>{response.error}</p>
          </div>
        )}

        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Request Payload</h4>
            <button 
              onClick={() => copyToClipboard(JSON.stringify(response.requestPayload, null, 2))}
              className="text-xs text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
            >
              <Copy className="w-3 h-3" /> Copy
            </button>
          </div>
          <pre className="bg-slate-50 p-3 rounded-lg text-sm font-mono overflow-x-auto border border-slate-100 max-h-40">
            {JSON.stringify(response.requestPayload, null, 2)}
          </pre>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Response Body</h4>
            <button 
              onClick={() => copyToClipboard(JSON.stringify(response.data, null, 2))}
              className="text-xs text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
            >
              <Copy className="w-3 h-3" /> Copy
            </button>
          </div>
          <pre className="bg-slate-50 p-3 rounded-lg text-sm font-mono overflow-x-auto border border-slate-100 flex-1">
            {JSON.stringify(response.data, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};
