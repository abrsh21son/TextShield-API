from flask import Blueprint, jsonify, request

from middleware.api_auth import resolve_user_from_api_key
from services.analyzer import analyze_text
from services.usage import record_analysis
from utility.database.main import get_session

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/api/demo-analyze", methods=["POST"])
def demo_analyze():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    if not str(text).strip():
        return jsonify({"success": False, "error": "text is required"}), 400
    try:
        analysis = analyze_text(str(text))
        return jsonify(analysis), 200
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@analyze_bp.route("/api/analyze", methods=["POST"])
def analyze():
    db = get_session()
    try:
        user, error = resolve_user_from_api_key(db, request)
        if error:
            status = 402 if error == "Insufficient credits" else 401
            return jsonify({"success": False, "error": error}), status

        payload = request.get_json(silent=True) or {}
        text = payload.get("text", "")
        if not str(text).strip():
            return jsonify({"success": False, "error": "text is required"}), 400

        analysis = analyze_text(str(text))
        record_analysis(
            db,
            user_id=user.id,
            input_text=str(text),
            is_profane=analysis["is_profane"],
            toxicity_score=analysis["toxicity_score"],
            endpoint="/api/analyze",
            ip_address=request.remote_addr or "0.0.0.0",
            status_code=200,
            deduct_credit=request.headers.get("x-demo", "").lower() != "true",
        )
        return jsonify(analysis), 200
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        db.rollback()
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        db.close()
