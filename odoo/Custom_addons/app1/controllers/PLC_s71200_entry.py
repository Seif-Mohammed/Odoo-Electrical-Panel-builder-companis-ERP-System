# controllers/main.py

from odoo import http
from odoo.http import request
import json
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class PlcDataController(http.Controller):
    @http.route('/plc/entry', type='json', auth='none', methods=['POST'], csrf=False)
    def plc_data_entry(self):
        try:
            data = request.get_json_data()
            PlcData = request.env['plc.data'].sudo()
            
            # Parse timestamp - handle both string and datetime formats
            timestamp = data.get('timestamp')
            if isinstance(timestamp, str):
                try:
                    # Parse ISO format timestamp
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    # If parsing fails, use current time
                    timestamp = datetime.now()
            elif not timestamp:
                timestamp = datetime.now()
            
            # Extract PLC info
            plc_info = data.get('plc', {})
            plc_ip = plc_info.get('ip', 'Unknown')
            plc_rack = plc_info.get('rack', 0)
            plc_slot = plc_info.get('slot', 0)
            
            # Extract and parse inputs/outputs
            inputs = data.get('inputs', {})
            outputs = data.get('outputs', {})
            
            # Count active inputs and outputs
            active_inputs = sum(1 for value in inputs.values() if value == 1)
            active_outputs = sum(1 for value in outputs.values() if value == 1)
            
            # Create new record with parsed data
            record = PlcData.create({
                'plc_ip': plc_ip,
                'plc_rack': plc_rack,
                'plc_slot': plc_slot,
                'timestamp': timestamp,
                'input_data': json.dumps(inputs, indent=2),
                'output_data': json.dumps(outputs, indent=2),
                'raw_data': json.dumps(data, indent=2),
                'active_inputs': active_inputs,
                'active_outputs': active_outputs,
                'total_inputs': len(inputs),
                'total_outputs': len(outputs),
                'api_key': data.get('api_key', ''),
            })
            
            _logger.info(f"PLC Data Entry Created - ID: {record.id}, IP: {plc_ip}, Active I/O: {active_inputs}/{active_outputs}")
            print(f"PLC Data Entry Created \n ID: {record.id}\n IP: {plc_ip}\n Active I/O: {active_inputs}/{active_outputs}")
            return {
                'status': 'success', 
                'message': 'Data received and processed',
                'record_id': record.id,
                'timestamp': timestamp.isoformat()
            }
            
        except Exception as e:
            _logger.error(f"Error processing PLC data: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @http.route('/plc/status', type='json', auth='none', methods=['GET'], csrf=False)
    def plc_status(self):
        """Get latest PLC status"""
        try:
            PlcData = request.env['plc.data'].sudo()
            latest_record = PlcData.search([], order='timestamp desc', limit=1)
            
            if latest_record:
                return {
                    'status': 'success',
                    'data': {
                        'plc_ip': latest_record.plc_ip,
                        'timestamp': latest_record.timestamp.isoformat(),
                        'active_inputs': latest_record.active_inputs,
                        'active_outputs': latest_record.active_outputs,
                        'last_update': latest_record.timestamp.isoformat()
                    }
                }
            else:
                return {'status': 'error', 'message': 'No PLC data found'}
                
        except Exception as e:
            _logger.error(f"Error getting PLC status: {str(e)}")
            return {'status': 'error', 'message': str(e)}