import Link from "next/link";
import type { ReactNode } from "react";

type AuthShellProps = {
  children: ReactNode;
  mode: "login" | "register";
};

export function AuthShell({ children, mode }: AuthShellProps) {
  const isLogin = mode === "login";

  return (
    <section className="auth-layout">
      <aside className="auth-intro">
        <div>
          <span className="eyebrow">Accreditation evidence intelligence</span>

          <h1>
            Turn institutional records into
            <span> review-ready evidence.</span>
          </h1>

          <p className="auth-lead">
            AccrediLens helps institutions organise uploaded documents,
            examine evidence with source-grounded AI, and identify gaps before
            formal accreditation review.
          </p>
        </div>

        <div className="auth-workflow" aria-label="AccrediLens workflow">
          <div className="workflow-item">
            <span className="workflow-number">01</span>
            <div>
              <strong>Collect evidence</strong>
              <p>Bring institutional PDFs into one structured evidence library.</p>
            </div>
          </div>

          <div className="workflow-item">
            <span className="workflow-number">02</span>
            <div>
              <strong>Review with context</strong>
              <p>Ask questions and inspect answers alongside their cited sources.</p>
            </div>
          </div>

          <div className="workflow-item">
            <span className="workflow-number">03</span>
            <div>
              <strong>Prepare decisions</strong>
              <p>Surface supporting evidence and gaps for informed human review.</p>
            </div>
          </div>
        </div>

        <p className="auth-principle">
          Evidence remains traceable. Human judgment remains in control.
        </p>
      </aside>

      <div className="auth-form-column">
        <div className="auth-form-card">
          <div className="auth-form-heading">
            <span className="form-kicker">
              {isLogin ? "Institutional workspace" : "Workspace registration"}
            </span>

            <h2>{isLogin ? "Welcome back" : "Create your account"}</h2>

            <p>
              {isLogin
                ? "Sign in to continue reviewing your institution?s accreditation evidence."
                : "Create an account to begin building your institutional evidence workspace."}
            </p>
          </div>

          {children}
        </div>

        <p className="auth-switch">
          {isLogin ? "New to AccrediLens?" : "Already have an account?"}{" "}
          <Link href={isLogin ? "/register" : "/login"}>
            {isLogin ? "Create an account" : "Sign in"}
          </Link>
        </p>
      </div>
    </section>
  );
}
