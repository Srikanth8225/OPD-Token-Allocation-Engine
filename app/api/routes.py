"""
API Routes for OPD Token Allocation Engine
"""
from flask import Blueprint, request, jsonify
from app.models import Doctor, TimeSlot
from app.services import AllocationService, ReallocationService
from app.utils.data_store import db

api_bp = Blueprint('api', __name__)

# Initialize services
allocation_service = AllocationService()
reallocation_service = ReallocationService()


@api_bp.route('/doctors', methods=['POST'])
def create_doctor():
    """Create a new doctor"""
    try:
        data = request.json
        doctor = Doctor(
            name=data['name'],
            specialization=data['specialization'],
            doctor_id=data.get('doctor_id'),
            active=data.get('active', True)
        )
        db.add_doctor(doctor)
        
        return jsonify({
            'success': True,
            'data': doctor.to_dict(),
            'message': 'Doctor created successfully'
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/doctors/<doctor_id>/slots', methods=['POST'])
def create_time_slots(doctor_id):
    """Create time slots for a doctor"""
    try:
        data = request.json
        doctor = db.get_doctor(doctor_id)
        
        if not doctor:
            return jsonify({
                'success': False,
                'error': f'Doctor not found: {doctor_id}'
            }), 404
        
        slots_created = []
        
        # Support creating multiple slots at once
        slots_data = data if isinstance(data, list) else [data]
        
        for slot_data in slots_data:
            slot = TimeSlot(
                doctor_id=doctor_id,
                start_time=slot_data['start_time'],
                end_time=slot_data['end_time'],
                date=slot_data['date'],
                max_capacity=slot_data.get('max_capacity', 10),
                slot_id=slot_data.get('slot_id')
            )
            db.add_time_slot(slot)
            slots_created.append(slot.to_dict())
        
        return jsonify({
            'success': True,
            'data': slots_created,
            'message': f'{len(slots_created)} slot(s) created successfully'
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/doctors/<doctor_id>/slots', methods=['GET'])
def get_doctor_slots(doctor_id):
    """Get all slots for a doctor"""
    try:
        date_filter = request.args.get('date')
        slots = db.get_slots_by_doctor(doctor_id, date_filter)
        
        return jsonify({
            'success': True,
            'data': [slot.to_dict() for slot in slots],
            'count': len(slots)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/tokens/allocate', methods=['POST'])
def allocate_token():
    """Allocate a new token"""
    try:
        data = request.json
        
        token, status_msg = allocation_service.allocate_token(
            patient_data=data['patient'],
            doctor_id=data['doctor_id'],
            date=data['date'],
            preferred_slot_time=data['preferred_slot_time'],
            source=data['source']
        )
        
        patient = db.get_patient(token.patient_id)
        doctor = db.get_doctor(token.doctor_id)
        slot = db.get_time_slot(token.slot_id)
        
        response_data = {
            'token_id': token.id,
            'token_number': token.token_number,
            'status': token.status,
            'patient_name': patient.name if patient else 'Unknown',
            'doctor_name': doctor.name if doctor else 'Unknown',
            'slot_time': f"{slot.start_time} - {slot.end_time}" if slot else 'Unknown',
            'date': slot.date if slot else 'Unknown',
            'estimated_time': token.estimated_time,
            'source': token.source,
            'priority': token.priority
        }
        
        if token.status == 'WAITLISTED':
            waitlist_pos = allocation_service.queue_manager.get_waitlist_position(token.slot_id, token.id)
            response_data['waitlist_position'] = waitlist_pos
            response_data['estimated_wait'] = f"{waitlist_pos * 5} minutes"  # Rough estimate
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': status_msg
        }), 201 if token.status == 'CONFIRMED' else 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/tokens/emergency', methods=['POST'])
def allocate_emergency_token():
    """Allocate an emergency token (highest priority)"""
    try:
        data = request.json
        
        token, status_msg = allocation_service.allocate_emergency_token(
            patient_data=data['patient'],
            doctor_id=data['doctor_id'],
            date=data['date'],
            preferred_slot_time=data['preferred_slot_time']
        )
        
        patient = db.get_patient(token.patient_id)
        doctor = db.get_doctor(token.doctor_id)
        slot = db.get_time_slot(token.slot_id)
        
        response_data = {
            'token_id': token.id,
            'token_number': token.token_number,
            'status': token.status,
            'patient_name': patient.name if patient else 'Unknown',
            'doctor_name': doctor.name if doctor else 'Unknown',
            'slot_time': f"{slot.start_time} - {slot.end_time}" if slot else 'Unknown',
            'date': slot.date if slot else 'Unknown',
            'estimated_time': token.estimated_time,
            'source': 'EMERGENCY',
            'priority': token.priority
        }
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': status_msg
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/tokens/<token_id>/cancel', methods=['POST'])
def cancel_token(token_id):
    """Cancel a token"""
    try:
        result = reallocation_service.cancel_token(token_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': result['message']
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/tokens/<token_id>/no-show', methods=['POST'])
def mark_no_show(token_id):
    """Mark a token as no-show"""
    try:
        result = reallocation_service.mark_no_show(token_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': result['message']
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/tokens/<token_id>/complete', methods=['POST'])
def complete_token(token_id):
    """Mark a token as completed"""
    try:
        result = reallocation_service.complete_token(token_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': result['message']
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/tokens/<token_id>', methods=['GET'])
def get_token_details(token_id):
    """Get detailed token information"""
    try:
        details = reallocation_service.get_token_details(token_id)
        
        return jsonify({
            'success': True,
            'data': details
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/slots/<slot_id>/status', methods=['GET'])
def get_slot_status(slot_id):
    """Get slot status with queue details"""
    try:
        status = allocation_service.get_slot_status(slot_id)
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/stats', methods=['GET'])
def get_system_stats():
    """Get overall system statistics"""
    try:
        stats = db.get_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@api_bp.route('/doctors', methods=['GET'])
def get_all_doctors():
    """Get all doctors"""
    try:
        doctors = db.get_all_doctors()
        
        return jsonify({
            'success': True,
            'data': [doctor.to_dict() for doctor in doctors],
            'count': len(doctors)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# Health check endpoint
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'OPD Token Allocation Engine is running',
        'version': '1.0.0'
    }), 200
