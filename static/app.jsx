const { useState, useEffect, useMemo } = React;
const { motion, AnimatePresence } = window.Motion;
const { PieChart, Pie, Cell, RadialBarChart, RadialBar, ResponsiveContainer, Tooltip: RechartsTooltip } = window.Recharts;

// API Base URL
const API_BASE = '/api';

const apiFetch = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  const headers = { ...options.headers };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.reload();
  }
  return response;
};



// --- Auth Components ---
const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const res = await fetch(`${API_BASE}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        onLogin(data.access_token);
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  return (
    <div className="flex items-center justify-center" style={{ height: '100vh', width: '100vw', backgroundColor: 'var(--bg-base)' }}>
      <div className="card" style={{ width: '400px', padding: '2rem' }}>
        <h2 className="text-center mb-6 text-ai">PO Guardian Login</h2>
        <form onSubmit={handleSubmit} className="flex-col gap-4">
          <input 
            type="text" 
            placeholder="Username" 
            value={username} 
            onChange={e => setUsername(e.target.value)} 
            required 
            style={{ padding: '0.75rem', borderRadius: '4px', border: '1px solid var(--border)', backgroundColor: 'var(--bg-surface-highlight)', color: '#fff' }}
          />
          <input 
            type="password" 
            placeholder="Password" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            required 
            style={{ padding: '0.75rem', borderRadius: '4px', border: '1px solid var(--border)', backgroundColor: 'var(--bg-surface-highlight)', color: '#fff' }}
          />
          {error && <div style={{ color: 'var(--status-rejected)' }}>{error}</div>}
          <button type="submit" className="btn btn-primary" style={{ padding: '0.75rem' }}>Login</button>
        </form>
      </div>
    </div>
  );
};

// --- Utility Components ---
const StatusBadge = ({ status }) => {
  let cls = 'badge ';
  let icon = '';
  if (status === 'Ready for Payment') { cls += 'badge-ready'; icon = '✅'; }
  else if (status === 'Paid') { cls += 'badge-ready'; icon = '💰'; }
  else if (status === 'Procurement Review') { cls += 'badge-review'; icon = '⚠️'; }
  else if (status === 'Rejected') { cls += 'badge-rejected'; icon = '❌'; }
  else { cls += 'badge-ai'; }

  return <span className={cls}>{icon} {status}</span>;
};

// --- Page Components ---

// 1. Pipeline Dashboard
const PipelineDashboard = ({ onNavigate }) => {
  const [stats, setStats] = useState({ total: 0, ready: 0, review: 0, rejected: 0 });
  const [isDemoRunning, setIsDemoRunning] = useState(false);
  const [activeNode, setActiveNode] = useState(null);

  const nodes = [
    { id: 1, name: "Inbox Watcher" },
    { id: 2, name: "PDF Extract" },
    { id: 3, name: "AI Extraction" },
    { id: 4, name: "PO Retrieval" },
    { id: 5, name: "Field Match" },
    { id: 6, name: "Discrepancies" },
    { id: 7, name: "Validation" },
    { id: 8, name: "Stored" }
  ];

  const fetchStats = async () => {
    try {
      const res = await apiFetch(`${API_BASE}/invoices`);
      const data = await res.json();
      setStats({
        total: data.length,
        ready: data.filter(d => d.validation_status === 'Ready for Payment').length,
        review: data.filter(d => d.validation_status === 'Procurement Review').length,
        rejected: data.filter(d => d.validation_status === 'Rejected').length,
      });
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const runDemo = async () => {
    setIsDemoRunning(true);
    // Animate pipeline
    for (let i = 1; i <= 8; i++) {
      setActiveNode(i);
      await new Promise(r => setTimeout(r, 600)); // 600ms per node
    }
    setActiveNode(null);

    // Call API (happens in background mostly)
    try {
      await apiFetch(`${API_BASE}/ingest`, { method: 'POST' });
    } catch (e) {
      console.error(e);
    }
    await fetchStats();
    setIsDemoRunning(false);
  };

  const pieData = [
    { name: 'Ready', value: stats.ready, color: '#10b981' },
    { name: 'Review', value: stats.review, color: '#f59e0b' },
    { name: 'Rejected', value: stats.rejected, color: '#ef4444' }
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex-col gap-6">
      <div className="flex justify-between items-center mb-4">
        <h2>Pipeline Overview</h2>
        <button className="btn btn-primary" onClick={runDemo} disabled={isDemoRunning}>
          {isDemoRunning ? "Processing..." : "▶ Run Ingestion Demo"}
        </button>
      </div>

      {/* Pipeline Visualization */}
      <div className="card" style={{ padding: '3rem 2rem', position: 'relative', overflow: 'hidden' }}>
        <h3 className="text-secondary text-sm uppercase mb-6" style={{ position: 'absolute', top: '1rem' }}>AI Processing Flow</h3>
        <div className="flex justify-between items-center" style={{ position: 'relative' }}>
          {/* Connecting Line */}
          <div style={{ position: 'absolute', top: '50%', left: '5%', right: '5%', height: '4px', backgroundColor: 'var(--border)', zIndex: 0, transform: 'translateY(-50%)', borderRadius: '2px' }}></div>
          
          {nodes.map(node => (
            <div key={node.id} className="flex-col items-center gap-2" style={{ zIndex: 1, width: '12%' }}>
              <motion.div
                animate={{
                  backgroundColor: activeNode === node.id ? 'var(--color-ai)' : 'var(--bg-surface-highlight)',
                  boxShadow: activeNode === node.id ? '0 0 20px var(--color-ai)' : '0 0 0px transparent',
                  scale: activeNode === node.id ? 1.2 : 1
                }}
                style={{
                  width: '24px', height: '24px', borderRadius: '50%', border: '2px solid var(--border)'
                }}
              />
              <span className="text-xs text-center" style={{ color: activeNode === node.id ? '#fff' : 'var(--text-secondary)', fontWeight: activeNode === node.id ? 'bold' : 'normal' }}>
                {node.name}
              </span>
            </div>
          ))}

          {/* Moving dot */}
          {activeNode && (
            <motion.div
              initial={false}
              animate={{ left: `${((activeNode - 1) / (nodes.length - 1)) * 90 + 5}%` }}
              transition={{ type: "spring", stiffness: 100, damping: 20 }}
              style={{
                position: 'absolute', top: '50%', transform: 'translate(-50%, -50%)',
                width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#fff',
                boxShadow: '0 0 10px #fff', zIndex: 2
              }}
            />
          )}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        <div className="card">
          <h4 className="text-secondary text-sm uppercase">Total Invoices</h4>
          <div className="text-xl font-bold">{stats.total}</div>
        </div>
        <div className="card" style={{ borderLeft: '4px solid var(--status-ready)' }}>
          <h4 className="text-secondary text-sm uppercase">Ready for Payment</h4>
          <div className="text-xl font-bold" style={{ color: 'var(--status-ready)' }}>{stats.ready}</div>
        </div>
        <div className="card" style={{ borderLeft: '4px solid var(--status-review)' }}>
          <h4 className="text-secondary text-sm uppercase">Needs Review</h4>
          <div className="text-xl font-bold" style={{ color: 'var(--status-review)' }}>{stats.review}</div>
        </div>
        <div className="card" style={{ borderLeft: '4px solid var(--status-rejected)' }}>
          <h4 className="text-secondary text-sm uppercase">Rejected</h4>
          <div className="text-xl font-bold" style={{ color: 'var(--status-rejected)' }}>{stats.rejected}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="card flex items-center justify-center" style={{ height: '300px' }}>
          {stats.total > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip contentStyle={{ backgroundColor: 'var(--bg-surface)', border: 'none', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-muted">No data yet</p>
          )}
        </div>
        <div className="card flex-col justify-center">
          <h3>Ready to start?</h3>
          <p className="text-secondary">Run the demo to ingest sample PDFs, or view the current invoice list.</p>
          <button className="btn btn-outline mt-4" style={{ width: 'fit-content' }} onClick={() => onNavigate('list')}>
            View All Invoices &rarr;
          </button>
        </div>
      </div>
    </motion.div>
  );
};

// 2. Invoice List
const InvoiceList = ({ onNavigate }) => {
  const [invoices, setInvoices] = useState([]);
  const [filter, setFilter] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    apiFetch(`${API_BASE}/invoices${filter ? `?status=${encodeURIComponent(filter)}` : ''}`)
      .then(r => r.json())
      .then(setInvoices)
      .catch(console.error);
  }, [filter]);

  const filteredInvoices = useMemo(() => {
    return invoices.filter(inv => 
      (inv.vendor_name || "").toLowerCase().includes(search.toLowerCase()) ||
      (inv.invoice_number || "").toLowerCase().includes(search.toLowerCase())
    );
  }, [invoices, search]);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-col gap-6">
      <div className="flex justify-between items-center">
        <h2>Invoices</h2>
        <div className="flex gap-4">
          <input 
            type="text" 
            placeholder="Search vendor or invoice #..." 
            value={search} 
            onChange={e => setSearch(e.target.value)} 
            style={{ width: '250px' }}
          />
          <select value={filter} onChange={e => setFilter(e.target.value)} style={{ width: '200px' }}>
            <option value="">All Statuses</option>
            <option value="Ready for Payment">Ready for Payment</option>
            <option value="Paid">Paid</option>
            <option value="Procurement Review">Procurement Review</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <AnimatePresence>
          {filteredInvoices.map((inv, i) => (
            <motion.div
              key={inv.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ y: -5, boxShadow: 'var(--shadow-lg)' }}
              className="card flex-col justify-between cursor-pointer"
              onClick={() => onNavigate('detail', inv.id)}
            >
              <div>
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold" style={{ margin: 0 }}>{inv.vendor_name || "Unknown Vendor"}</h4>
                  <span className="text-muted text-xs">#{inv.id}</span>
                </div>
                <p className="text-secondary text-sm mb-4">Inv: {inv.invoice_number || '-'} &bull; PO: {inv.purchase_order_number || '-'}</p>
                <div className="text-lg font-medium mb-4">{inv.gross_amount !== null ? `${inv.gross_amount} ${inv.currency || ''}` : '-'}</div>
              </div>
              <div>
                <StatusBadge status={inv.validation_status} />
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {filteredInvoices.length === 0 && (
          <div className="text-muted col-span-3">No invoices found matching criteria.</div>
        )}
      </div>
    </motion.div>
  );
};

// 3. Invoice Detail
const InvoiceDetail = ({ id, onNavigate }) => {
  const [invoice, setInvoice] = useState(null);
  const [logs, setLogs] = useState([]);
  const [comments, setComments] = useState("");

  const loadData = async () => {
    try {
      const invRes = await apiFetch(`${API_BASE}/invoices/${id}`);
      const invData = await invRes.json();
      setInvoice(invData);
      setComments(invData.reviewer_comments || "");

      const logRes = await apiFetch(`${API_BASE}/audit-log/${id}`);
      setLogs(await logRes.json());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => { loadData(); }, [id]);

  const handleReview = async (decision) => {
    if (decision === 'reject' && !comments.trim()) {
      alert("Please provide a rejection reason in the comments.");
      return;
    }
    await apiFetch(`${API_BASE}/invoices/${id}/review`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, reviewer_comments: comments, actor: "demo_reviewer" })
    });
    loadData();
  };

  const handlePay = async () => {
    await apiFetch(`${API_BASE}/invoices/${id}/pay`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ actor: "demo_user" })
    });
    loadData();
  };

  if (!invoice) return <div>Loading...</div>;

  const confScore = invoice.confidence_score ? Math.round(invoice.confidence_score * 100) : 0;
  const confColor = confScore > 85 ? '#10b981' : confScore > 60 ? '#f59e0b' : '#ef4444';
  const confData = [{ name: 'Confidence', value: confScore, fill: confColor }];

  return (
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="flex-col gap-6 pb-10">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <button className="btn btn-outline" onClick={() => onNavigate('list')}>&larr; Back</button>
          <h2 style={{ margin: 0 }}>Invoice #{invoice.invoice_number || invoice.id}</h2>
          {invoice.invoice_attachment_path && (
            <a href={`${API_BASE}/invoices/${invoice.id}/pdf`} target="_blank" rel="noreferrer" className="btn btn-outline" style={{ marginLeft: '1rem' }}>
              📄 View PDF
            </a>
          )}
        </div>
        <StatusBadge status={invoice.validation_status} />
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="col-span-2 flex-col gap-6">
          
          {/* AI Extracted Data Panel */}
          <div className="card" style={{ borderLeft: '4px solid var(--color-ai)', background: 'linear-gradient(90deg, rgba(0, 229, 255, 0.05) 0%, transparent 100%)' }}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-ai flex items-center gap-2"><span className="badge badge-ai">AI</span> Extracted Data</h3>
              <div style={{ width: '80px', height: '80px', position: 'relative' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="100%" barSize={8} data={confData} startAngle={90} endAngle={-270}>
                    <RadialBar background={{ fill: 'rgba(255,255,255,0.1)' }} dataKey="value" cornerRadius={10} />
                  </RadialBarChart>
                </ResponsiveContainer>
                <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontSize: '0.85rem', fontWeight: 'bold' }}>
                  {confScore}%
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-secondary">Vendor:</span> {invoice.vendor_name || '-'}</div>
              <div><span className="text-secondary">PO Number:</span> {invoice.purchase_order_number || '-'}</div>
              <div><span className="text-secondary">Date:</span> {invoice.invoice_date || '-'}</div>
              <div><span className="text-secondary">Gross Amt:</span> {invoice.gross_amount} {invoice.currency}</div>
              <div><span className="text-secondary">Received At:</span> {invoice.received_at ? new Date(invoice.received_at).toLocaleString() : '-'}</div>
              {invoice.payment_done_at && <div><span className="text-secondary">Paid At:</span> {new Date(invoice.payment_done_at).toLocaleString()}</div>}
            </div>
          </div>

          {/* Warnings Panel */}
          {invoice.extraction_warnings && invoice.extraction_warnings.length > 0 && (
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} className="card" style={{ border: '1px solid rgba(245, 158, 11, 0.5)', backgroundColor: 'rgba(245, 158, 11, 0.05)' }}>
              <h3 className="text-review mb-2" style={{ color: '#f59e0b' }}>⚠️ Extraction Warnings</h3>
              <ul className="text-sm" style={{ paddingLeft: '1.5rem', color: '#fcd34d' }}>
                {invoice.extraction_warnings.map((w, i) => <li key={i}>{w}</li>)}
              </ul>
            </motion.div>
          )}

          {/* Comparison Table */}
          <div className="card">
            <h3 className="mb-4">Invoice vs. PO Comparison</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Field</th>
                    <th>Extracted (Invoice)</th>
                    <th>Expected (PO)</th>
                    <th>Match</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.purchase_order_match?.fields ? (
                    invoice.purchase_order_match.fields.map((f, i) => (
                      <tr key={i} className={f.matched ? "row-match" : "row-mismatch"}>
                        <td className="font-medium">{f.field_name}</td>
                        <td>{f.invoice_value !== null ? f.invoice_value : '-'}</td>
                        <td>{f.po_value !== null ? f.po_value : '-'}</td>
                        <td>
                          {f.matched ? (
                            <span className="text-ready" style={{ color: 'var(--status-ready)' }}>✅ Yes</span>
                          ) : (
                            <span className="text-rejected" style={{ color: 'var(--status-rejected)' }}>❌ No</span>
                          )}
                          {f.difference_percent > 0 && (
                            <span className="ml-2 badge" style={{ marginLeft: '0.5rem', backgroundColor: 'rgba(255,255,255,0.1)' }}>
                              {f.difference_percent.toFixed(1)}% diff
                            </span>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr><td colSpan="4" className="text-muted text-center">No comparison data available (Missing PO).</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Discrepancies */}
          <div className="card">
            <h3 className="mb-4">Identified Discrepancies</h3>
            <div className="flex-col gap-4">
              {invoice.discrepancy_summary && invoice.discrepancy_summary.length > 0 ? (
                invoice.discrepancy_summary.map((d, i) => (
                  <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} 
                    className="p-4" style={{ backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 'var(--radius-sm)', borderLeft: `3px solid ${d.severity === 'major' ? 'var(--status-rejected)' : 'var(--status-review)'}` }}>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="badge" style={{ backgroundColor: d.severity === 'major' ? 'var(--status-rejected)' : 'transparent', border: d.severity === 'minor' ? '1px solid var(--status-review)' : 'none', color: d.severity === 'minor' ? 'var(--status-review)' : '#fff' }}>
                        {d.severity.toUpperCase()}
                      </span>
                      <strong className="text-sm uppercase text-secondary">{d.type}</strong>
                    </div>
                    <p className="text-sm" style={{ margin: 0 }}>{d.description}</p>
                  </motion.div>
                ))
              ) : (
                <p className="text-muted">No discrepancies found.</p>
              )}
            </div>
          </div>

        </div>

        {/* Right Column */}
        <div className="flex-col gap-6">
          
          {/* Verdict */}
          <div className="card text-center" style={{ boxShadow: `0 0 20px ${invoice.validation_status === 'Ready for Payment' ? 'rgba(16, 185, 129, 0.2)' : invoice.validation_status === 'Rejected' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)'}` }}>
            <h3 className="text-secondary text-sm uppercase mb-2">Final Verdict</h3>
            <div className="mb-4"><StatusBadge status={invoice.validation_status} /></div>
            <p className="text-sm text-muted">
              {invoice.validation_status === 'Ready for Payment' && "Clean match. Ready for ERP export."}
              {invoice.validation_status === 'Paid' && "Payment has been processed."}
              {invoice.validation_status === 'Rejected' && "Major discrepancies detected. Do not pay."}
              {invoice.validation_status === 'Procurement Review' && "Minor deviations found. Human review needed."}
            </p>
          </div>

          {/* Review Panel */}
          {invoice.validation_status === 'Ready for Payment' ? (
            <div className="card">
              <h3 className="text-secondary text-sm uppercase mb-4">Payment Actions</h3>
              <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="btn btn-primary w-full" onClick={handlePay}>Mark as Paid</motion.button>
            </div>
          ) : invoice.validation_status !== 'Paid' ? (
            <div className="card">
              <h3 className="text-secondary text-sm uppercase mb-4">Manual Override</h3>
              <textarea 
                rows="3" 
                placeholder="Add reviewer comments..." 
                value={comments} 
                onChange={e => setComments(e.target.value)}
                className="mb-4"
              ></textarea>
              <div className="flex gap-4">
                <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="btn btn-success flex-1" onClick={() => handleReview('approve')}>Approve</motion.button>
                <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="btn btn-danger flex-1" onClick={() => handleReview('reject')}>Reject</motion.button>
              </div>
            </div>
          ) : null}

          {/* Audit Trail */}
          <div className="card">
            <h3 className="text-secondary text-sm uppercase mb-4">Audit Trail</h3>
            <div className="flex-col gap-4">
              {logs.map((log, i) => (
                <div key={i} className="flex gap-4" style={{ position: 'relative' }}>
                  <div style={{ width: '2px', backgroundColor: 'var(--border)', position: 'absolute', left: '5px', top: '20px', bottom: '-20px', zIndex: 0, display: i === logs.length - 1 ? 'none' : 'block' }}></div>
                  <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: 'var(--color-ai)', zIndex: 1, marginTop: '5px' }}></div>
                  <div className="flex-1">
                    <div className="text-xs text-muted mb-1">{new Date(log.timestamp).toLocaleString()}</div>
                    <div className="text-sm font-medium">{log.action}</div>
                    <div className="text-xs text-secondary">{log.actor}</div>
                    {log.old_value !== log.new_value && (
                      <div className="text-xs mt-1 p-2" style={{ backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: '4px' }}>
                        {log.old_value || 'None'} &rarr; {log.new_value}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </motion.div>
  );
};

// 4. Monitoring Page
const MonitoringPage = () => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchLogs = () => {
      apiFetch(`${API_BASE}/logs/recent`)
        .then(r => r.json())
        .then(setLogs)
        .catch(console.error);
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-col gap-4 h-full">
      <h2>System Logs</h2>
      <div className="terminal flex-1" style={{ minHeight: '600px' }}>
        {logs.map((log, i) => (
          <div key={i} style={{ marginBottom: '4px' }}>
            <span className="log-time">[{log.timestamp}]</span>{' '}
            <span className={`log-${log.level ? log.level.toLowerCase() : 'info'}`}>[{log.level}]</span>{' '}
            <span className="log-module">({log.module})</span>{' '}
            <span>{log.message}</span>
            {log.invoice_id && <span style={{ color: '#a78bfa' }}> [Inv: {log.invoice_id}]</span>}
            {log.duration_ms && <span style={{ color: '#34d399' }}> ({log.duration_ms}ms)</span>}
          </div>
        ))}
        {logs.length === 0 && <div className="text-muted">Waiting for logs...</div>}
      </div>
    </motion.div>
  );
};

// --- App Layout ---

const App = () => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [view, setView] = useState({ name: 'dashboard', param: null });

  if (!token) {
    return <Login onLogin={setToken} />;
  }

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };


  const navigate = (name, param = null) => {
    setView({ name, param });
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <nav className="sidebar">
        <div className="flex items-center gap-2 mb-6 p-2">
          <div style={{ width: '24px', height: '24px', backgroundColor: 'var(--color-ai)', borderRadius: '4px' }}></div>
          <h2 className="text-lg" style={{ margin: 0 }}>PO Guardian</h2>
        </div>
        
        <button className={`btn ${view.name === 'dashboard' ? 'btn-primary' : 'btn-outline'}`} style={{ justifyContent: 'flex-start' }} onClick={() => navigate('dashboard')}>
          Dashboard
        </button>
        <button className={`btn ${view.name === 'list' || view.name === 'detail' ? 'btn-primary' : 'btn-outline'}`} style={{ justifyContent: 'flex-start' }} onClick={() => navigate('list')}>
          Invoices
        </button>
        <button className={`btn ${view.name === 'monitor' ? 'btn-primary' : 'btn-outline'}`} style={{ justifyContent: 'flex-start' }} onClick={() => navigate('monitor')}>
          System Logs
        </button>
      
        <button className="btn btn-outline" style={{ justifyContent: 'flex-start', marginTop: 'auto', border: 'none', color: 'var(--status-rejected)' }} onClick={logout}>
          Logout
        </button>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        <AnimatePresence mode="wait">
          {view.name === 'dashboard' && <PipelineDashboard key="dashboard" onNavigate={navigate} />}
          {view.name === 'list' && <InvoiceList key="list" onNavigate={navigate} />}
          {view.name === 'detail' && <InvoiceDetail key="detail" id={view.param} onNavigate={navigate} />}
          {view.name === 'monitor' && <MonitoringPage key="monitor" />}
        </AnimatePresence>
      </main>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
