from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Polisi Keselamatan Kandungan (CSP)
        # Kita benarkan:
        # - 'self': Sumber dari domain kita sendiri (termasuk /static)
        # - https://cdn.jsdelivr.net: Untuk memuat turun TailwindCSS
        csp_policy = [
            "default-src 'self'",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net", # Benarkan style dari CDN dan inline
            "script-src 'self' 'unsafe-inline'", # Benarkan skrip dari domain sendiri & inline
            "img-src 'self' data:", # Benarkan imej dari domain sendiri
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'"
        ]
        
        headers = {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "; ".join(csp_policy),
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        response.headers.update(headers)
        return response
