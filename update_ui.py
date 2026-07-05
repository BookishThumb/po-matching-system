import os

FILE_PATH = r"c:\Users\rouna\OneDrive\Desktop\invoicewatch\po-matching-system\static\app.jsx"

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add LogoIcon
logo_svg = """
const LogoIcon = () => (
  <svg width="60%" height="60%" viewBox="0 0 24 24" fill="none" stroke="#131826" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  </svg>
);

// --- Auth Components ---
"""
content = content.replace("// --- Auth Components ---", logo_svg, 1)

# 2. Update Login Component
old_login = """const Login = ({ onLogin, onBack }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) return;
    setLoading(true);
    setError('');
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const res = await fetch(`/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        sessionStorage.setItem('token', data.access_token);
        onLogin(data.access_token);
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Connection error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center" style={{ minHeight: '100vh', width: '100vw', backgroundColor: 'var(--bg-base)' }}>
      <button className="btn btn-outline" style={{ position: 'absolute', top: '2rem', left: '2rem' }} onClick={onBack}>
        &larr; Back to Home
      </button>
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 20 }} 
        animate={{ opacity: 1, scale: 1, y: 0 }} 
        transition={{ duration: 0.4 }}
        className="card" style={{ width: '400px', padding: '2.5rem', boxShadow: '0 0 40px rgba(0, 229, 255, 0.1)' }}
      >
        <div className="flex justify-center mb-4">
          <div style={{ width: '48px', height: '48px', backgroundColor: 'rgba(0, 229, 255, 0.1)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--color-ai)' }}>
             <i data-lucide="lock" style={{ color: 'var(--color-ai)' }}></i>
          </div>
        </div>
        <h2 className="text-center mb-6 text-ai">Welcome Back</h2>
        
        {error && (
          <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '0.75rem', borderRadius: '8px', color: 'var(--status-rejected)', marginBottom: '1.5rem', textAlign: 'center', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex-col gap-4">
          <div className="flex-col gap-1">
            <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Username</label>
            <input 
              type="text" 
              placeholder="Enter your username" 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              required 
              style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)', backgroundColor: 'var(--bg-surface-highlight)', color: '#fff', outline: 'none', transition: 'border-color 0.2s' }}
              onFocus={(e) => e.target.style.borderColor = 'var(--color-ai)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--border)'}
            />
          </div>
          <div className="flex-col gap-1 mb-2">
            <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Password</label>
            <input 
              type="password" 
              placeholder="Enter your password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
              style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)', backgroundColor: 'var(--bg-surface-highlight)', color: '#fff', outline: 'none', transition: 'border-color 0.2s' }}
              onFocus={(e) => e.target.style.borderColor = 'var(--color-ai)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--border)'}
            />
          </div>
          
          <motion.button 
            whileHover={!loading ? { y: -1, filter: 'brightness(1.1)' } : {}}
            whileTap={!loading ? { scale: 0.98 } : {}}
            type="submit" 
            className="btn" 
            style={{ padding: '0.875rem', backgroundColor: 'var(--color-ai)', color: '#000', fontWeight: 'bold', display: 'flex', justifyContent: 'center', borderRadius: '8px', opacity: loading ? 0.7 : 1 }}
            disabled={loading}
          >
            {loading ? "Authenticating..." : "Sign In"}
          </motion.button>
        </form>

        <div className="text-center mt-6 text-xs text-muted" style={{ padding: '1rem', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
          <strong>Demo credentials:</strong><br/>
          Username: <code>admin</code> | Password: <code>password</code>
        </div>
      </motion.div>
    </div>
  );
};"""

new_login = """const Login = ({ onLogin, onBack }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) return;
    setLoading(true);
    setError('');
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const res = await fetch(`/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        sessionStorage.setItem('token', data.access_token);
        onLogin(data.access_token);
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Connection error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center" style={{ minHeight: '100vh', width: '100vw', backgroundColor: 'var(--bg-base)', position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', width: '800px', height: '800px', background: 'radial-gradient(circle, rgba(0,229,255,0.07) 0%, transparent 60%)', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 0 }}></div>
      <button className="btn btn-outline" style={{ position: 'absolute', top: '2rem', left: '2rem', zIndex: 10, background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(10px)' }} onClick={onBack}>
        &larr; Back to Home
      </button>
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 20 }} 
        animate={{ opacity: 1, scale: 1, y: 0 }} 
        transition={{ duration: 0.4 }}
        className="card" style={{ width: '420px', padding: '3rem', boxShadow: '0 0 40px rgba(0, 229, 255, 0.1)', zIndex: 1, backgroundColor: 'rgba(19, 24, 38, 0.8)', backdropFilter: 'blur(10px)' }}
      >
        <div className="flex justify-center mb-6">
          <div style={{ width: '56px', height: '56px', backgroundColor: 'var(--color-ai)', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
             <LogoIcon />
          </div>
        </div>
        <h2 className="text-center mb-8 text-ai text-2xl">Welcome Back</h2>
        
        {error && (
          <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '0.75rem', borderRadius: '8px', color: 'var(--status-rejected)', marginBottom: '1.5rem', textAlign: 'center', fontSize: '0.875rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex-col gap-5">
          <div className="flex-col gap-2">
            <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Username</label>
            <input 
              type="text" 
              placeholder="Enter your username" 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              required 
              style={{ padding: '0.875rem', borderRadius: '8px', border: '1px solid var(--border)', backgroundColor: 'var(--bg-surface-highlight)', color: '#fff', outline: 'none', transition: 'border-color 0.2s' }}
              onFocus={(e) => e.target.style.borderColor = 'var(--color-ai)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--border)'}
            />
          </div>
          <div className="flex-col gap-2 mb-2">
            <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Password</label>
            <input 
              type="password" 
              placeholder="Enter your password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
              style={{ padding: '0.875rem', borderRadius: '8px', border: '1px solid var(--border)', backgroundColor: 'var(--bg-surface-highlight)', color: '#fff', outline: 'none', transition: 'border-color 0.2s' }}
              onFocus={(e) => e.target.style.borderColor = 'var(--color-ai)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--border)'}
            />
          </div>
          
          <motion.button 
            whileHover={!loading ? { y: -1, filter: 'brightness(1.1)' } : {}}
            whileTap={!loading ? { scale: 0.98 } : {}}
            type="submit" 
            className="btn" 
            style={{ padding: '1rem', backgroundColor: 'var(--color-ai)', color: '#000', fontWeight: 'bold', display: 'flex', justifyContent: 'center', borderRadius: '8px', opacity: loading ? 0.7 : 1, fontSize: '1rem' }}
            disabled={loading}
          >
            {loading ? "Authenticating..." : "Sign In"}
          </motion.button>
        </form>

        <div className="mt-8 flex items-start gap-3" style={{ padding: '1rem', backgroundColor: 'var(--bg-surface-highlight)', borderRadius: '8px', border: '1px solid var(--border)' }}>
          <i data-lucide="info" style={{ color: 'var(--color-ai)', width: '20px', height: '20px', flexShrink: 0, marginTop: '2px' }}></i>
          <div className="text-xs text-secondary leading-relaxed">
            <strong className="text-primary block mb-1">Demo credentials:</strong>
            Username: <code style={{color: 'var(--color-ai)'}}>admin</code> | Password: <code style={{color: 'var(--color-ai)'}}>password</code>
          </div>
        </div>
      </motion.div>
    </div>
  );
};"""

if old_login in content:
    content = content.replace(old_login, new_login)
else:
    print("Failed to find old login component")

# 3. Update LandingPage Component
old_landing = """const LandingPage = ({ onNavigate }) => {
  useEffect(() => {
    window.lucide.createIcons();
  }, []);

  return (
    <div style={{ minHeight: '100vh', width: '100vw', backgroundColor: 'var(--bg-base)', overflowX: 'hidden' }}>
      {/* Navbar */}
      <nav className="flex justify-between items-center px-8 py-4 border-b border-[var(--border)] bg-[var(--bg-surface)]">
        <div className="flex items-center gap-3">
           <div style={{ width: '28px', height: '28px', backgroundColor: 'var(--color-ai)', borderRadius: '6px' }}></div>
           <h1 className="text-xl font-bold m-0" style={{ margin: 0 }}>PO Guardian</h1>
        </div>
        <div>
          <button className="btn btn-primary" onClick={() => onNavigate('login')}>Login to Dashboard</button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="flex-col items-center justify-center text-center py-24 px-4 relative" style={{ overflow: 'hidden' }}>
        <div style={{ position: 'absolute', width: '600px', height: '600px', background: 'radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 70%)', top: '-100px', left: '50%', transform: 'translateX(-50%)', zIndex: 0 }}></div>
        <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-5xl font-bold mb-6" style={{ zIndex: 1, maxWidth: '800px' }}>
          AI-Powered <span className="text-ai">Invoice Validation</span> & PO Matching
        </motion.h1>
        <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="text-xl text-secondary mb-10 max-w-2xl" style={{ zIndex: 1, maxWidth: '700px' }}>
          Automate your Accounts Payable. Extract data with Llama 3.3, match against Purchase Orders, and flag discrepancies instantly.
        </motion.p>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} style={{ zIndex: 1 }}>
          <button className="btn btn-primary" style={{ padding: '1rem 2rem', fontSize: '1.1rem' }} onClick={() => onNavigate('login')}>
            Enter Dashboard &rarr;
          </button>
        </motion.div>
      </section>

      {/* Features Grid */}
      <section className="py-16 px-8 max-w-6xl mx-auto">
        <h2 className="text-center text-3xl mb-12">Key Features</h2>
        <div className="grid grid-cols-3 gap-8">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="card" style={{ backgroundColor: 'var(--bg-surface)' }}>
            <i data-lucide="zap" style={{ color: 'var(--color-ai)', width: '32px', height: '32px', marginBottom: '1rem' }}></i>
            <h3 className="text-lg mb-2">AI-Powered Extraction</h3>
            <p className="text-secondary text-sm">LLM reads unstructured invoice PDFs and extracts structured line items, totals, and taxes accurately.</p>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }} className="card" style={{ backgroundColor: 'var(--bg-surface)' }}>
            <i data-lucide="file-search" style={{ color: '#10b981', width: '32px', height: '32px', marginBottom: '1rem' }}></i>
            <h3 className="text-lg mb-2">Automated PO Matching</h3>
            <p className="text-secondary text-sm">Field-by-field comparison against approved Purchase Orders with configurable tolerances.</p>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.2 }} className="card" style={{ backgroundColor: 'var(--bg-surface)' }}>
            <i data-lucide="shield" style={{ color: '#f59e0b', width: '32px', height: '32px', marginBottom: '1rem' }}></i>
            <h3 className="text-lg mb-2">Discrepancy Detection</h3>
            <p className="text-secondary text-sm">Instantly flags vendor mismatches, quantity/price errors, duplicates, and missing references.</p>
          </motion.div>
        </div>
      </section>

      {/* Tech Stack Strip */}
      <section className="py-8 border-t border-b border-[var(--border)] bg-[rgba(0,0,0,0.2)] mt-16">
        <div className="flex justify-center items-center gap-12 text-muted">
           <span className="flex items-center gap-2"><i data-lucide="code"></i> Python</span>
           <span className="flex items-center gap-2"><i data-lucide="zap"></i> FastAPI</span>
           <span className="flex items-center gap-2"><i data-lucide="cpu"></i> Groq (Llama 3.3)</span>
           <span className="flex items-center gap-2"><i data-lucide="database"></i> SQLite</span>
           <span className="flex items-center gap-2"><i data-lucide="layout"></i> React</span>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 text-center text-secondary text-sm">
        <p>Built for AnthraSync AI Engineer Assignment — Round 3</p>
      </footer>
    </div>
  );
};"""

new_landing = """const LandingPage = ({ onNavigate }) => {
  useEffect(() => {
    window.lucide.createIcons();
  }, []);

  return (
    <div style={{ minHeight: '100vh', width: '100vw', backgroundColor: 'var(--bg-base)', overflowX: 'hidden' }}>
      {/* Navbar */}
      <nav className="flex justify-center border-b border-[var(--border)] bg-[rgba(19,24,38,0.8)]" style={{ position: 'sticky', top: 0, zIndex: 50, backdropFilter: 'blur(10px)' }}>
        <div className="flex justify-between items-center w-full px-8 py-4" style={{ maxWidth: '1100px' }}>
          <div className="flex items-center gap-3">
             <div style={{ width: '32px', height: '32px', backgroundColor: 'var(--color-ai)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <LogoIcon />
             </div>
             <h1 className="text-xl font-bold m-0" style={{ margin: 0, letterSpacing: '-0.02em' }}>PO Guardian</h1>
          </div>
          <div className="flex items-center gap-8 text-sm">
            <a href="#features" className="text-secondary" style={{ textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={(e)=>e.target.style.color='#fff'} onMouseOut={(e)=>e.target.style.color='var(--text-secondary)'}>Features</a>
            <a href="#how-it-works" className="text-secondary" style={{ textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={(e)=>e.target.style.color='#fff'} onMouseOut={(e)=>e.target.style.color='var(--text-secondary)'}>How it Works</a>
            <button className="text-primary font-medium" style={{ background: 'none', border: 'none', cursor: 'pointer', transition: 'color 0.2s' }} onMouseOver={(e)=>e.target.style.color='var(--color-ai)'} onMouseOut={(e)=>e.target.style.color='var(--text-primary)'} onClick={() => onNavigate('login')}>Login</button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative w-full flex justify-center py-32 px-4 overflow-hidden" style={{ minHeight: '65vh', alignItems: 'center' }}>
        <div style={{ position: 'absolute', width: '1000px', height: '1000px', background: 'radial-gradient(circle, rgba(0,229,255,0.08) 0%, transparent 60%)', top: '-20%', left: '50%', transform: 'translateX(-50%)', zIndex: 0 }}></div>
        <div className="w-full text-center" style={{ zIndex: 1, maxWidth: '1100px' }}>
          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-5xl font-bold mb-6 mx-auto" style={{ maxWidth: '800px', lineHeight: 1.2, letterSpacing: '-0.02em' }}>
            AI-Powered <span className="text-ai">Invoice Validation</span> & PO Matching
          </motion.h1>
          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="text-xl text-secondary mb-10 mx-auto" style={{ maxWidth: '700px', lineHeight: 1.6 }}>
            Automate your Accounts Payable. Extract data with Llama 3.3, match against Purchase Orders, and flag discrepancies instantly.
          </motion.p>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <button className="btn btn-primary" style={{ padding: '1.25rem 2.5rem', fontSize: '1.1rem', borderRadius: '12px' }} onClick={() => onNavigate('login')}>
              Enter Dashboard &rarr;
            </button>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="w-full flex justify-center py-24 px-8" style={{ backgroundColor: 'var(--bg-surface)' }}>
        <div className="w-full" style={{ maxWidth: '1100px' }}>
          <h2 className="text-center text-3xl mb-12">Key Features</h2>
          <div className="grid grid-cols-3 gap-8">
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="card flex-col items-start" style={{ backgroundColor: 'var(--bg-base)', padding: '2.5rem 2rem', minHeight: '280px' }}>
              <div style={{ padding: '12px', backgroundColor: 'rgba(0,229,255,0.1)', borderRadius: '12px', marginBottom: '1.5rem', border: '1px solid rgba(0,229,255,0.2)' }}>
                <i data-lucide="zap" style={{ color: 'var(--color-ai)', width: '28px', height: '28px' }}></i>
              </div>
              <h3 className="text-xl mb-3">AI-Powered Extraction</h3>
              <p className="text-secondary" style={{ lineHeight: 1.6 }}>LLM reads unstructured invoice PDFs and extracts structured line items, totals, and taxes accurately.</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }} className="card flex-col items-start" style={{ backgroundColor: 'var(--bg-base)', padding: '2.5rem 2rem', minHeight: '280px' }}>
              <div style={{ padding: '12px', backgroundColor: 'rgba(16,185,129,0.1)', borderRadius: '12px', marginBottom: '1.5rem', border: '1px solid rgba(16,185,129,0.2)' }}>
                <i data-lucide="file-search" style={{ color: '#10b981', width: '28px', height: '28px' }}></i>
              </div>
              <h3 className="text-xl mb-3">Automated PO Matching</h3>
              <p className="text-secondary" style={{ lineHeight: 1.6 }}>Field-by-field comparison against approved Purchase Orders with configurable tolerances.</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.2 }} className="card flex-col items-start" style={{ backgroundColor: 'var(--bg-base)', padding: '2.5rem 2rem', minHeight: '280px' }}>
              <div style={{ padding: '12px', backgroundColor: 'rgba(245,158,11,0.1)', borderRadius: '12px', marginBottom: '1.5rem', border: '1px solid rgba(245,158,11,0.2)' }}>
                <i data-lucide="shield" style={{ color: '#f59e0b', width: '28px', height: '28px' }}></i>
              </div>
              <h3 className="text-xl mb-3">Discrepancy Detection</h3>
              <p className="text-secondary" style={{ lineHeight: 1.6 }}>Instantly flags vendor mismatches, quantity/price errors, duplicates, and missing references.</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="w-full flex justify-center py-24 px-8">
        <div className="w-full" style={{ maxWidth: '1100px' }}>
          <h2 className="text-center text-3xl mb-12">How It Works</h2>
          <div className="card" style={{ padding: '4rem 2rem', position: 'relative', overflow: 'hidden' }}>
            <div className="flex justify-between items-center" style={{ position: 'relative' }}>
              <div style={{ position: 'absolute', top: '35%', left: '5%', right: '5%', height: '2px', backgroundColor: 'var(--border)', zIndex: 0, transform: 'translateY(-50%)' }}></div>
              
              {[
                { id: 1, name: "Inbox Watcher" },
                { id: 2, name: "PDF Extract" },
                { id: 3, name: "AI Extraction" },
                { id: 4, name: "PO Retrieval" },
                { id: 5, name: "Field Match" },
                { id: 6, name: "Discrepancies" },
                { id: 7, name: "Validation" },
                { id: 8, name: "Stored" }
              ].map(node => (
                <div key={node.id} className="flex-col items-center gap-4" style={{ zIndex: 1, width: '12%' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '50%', border: '2px solid var(--color-ai)', backgroundColor: 'var(--bg-surface-highlight)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 'bold' }}>
                    {node.id}
                  </div>
                  <span className="text-xs text-center text-secondary font-medium">
                    {node.name}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack Strip */}
      <section className="w-full py-12 border-t border-[var(--border)] bg-[rgba(0,0,0,0.2)]">
        <div className="flex justify-center items-center gap-12 text-muted flex-wrap px-4">
           <span className="flex items-center gap-2"><i data-lucide="code"></i> Python</span>
           <span className="flex items-center gap-2"><i data-lucide="zap"></i> FastAPI</span>
           <span className="flex items-center gap-2"><i data-lucide="cpu"></i> Groq (Llama 3.3)</span>
           <span className="flex items-center gap-2"><i data-lucide="database"></i> SQLite</span>
           <span className="flex items-center gap-2"><i data-lucide="layout"></i> React</span>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full py-8 text-center text-secondary text-sm bg-[rgba(0,0,0,0.2)]">
        <p>Built for AnthraSync AI Engineer Assignment — Round 3</p>
      </footer>
    </div>
  );
};"""

if old_landing in content:
    content = content.replace(old_landing, new_landing)
else:
    print("Failed to find old landing component")

# 4. Fix App Sidebar Logo
old_sidebar_logo = """        <div className="flex items-center gap-2 mb-6 p-2">
          <div style={{ width: '24px', height: '24px', backgroundColor: 'var(--color-ai)', borderRadius: '4px' }}></div>
          <h2 className="text-lg" style={{ margin: 0 }}>PO Guardian</h2>
        </div>"""

new_sidebar_logo = """        <div className="flex items-center gap-3 mb-6 p-2">
          <div style={{ width: '28px', height: '28px', backgroundColor: 'var(--color-ai)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <LogoIcon />
          </div>
          <h2 className="text-lg" style={{ margin: 0 }}>PO Guardian</h2>
        </div>"""

if old_sidebar_logo in content:
    content = content.replace(old_sidebar_logo, new_sidebar_logo)
else:
    print("Failed to find sidebar logo")

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully!")
