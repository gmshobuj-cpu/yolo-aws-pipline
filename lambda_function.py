import json
import boto3
import urllib.request
from datetime import datetime

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('YoloDetectionResults')

def lambda_handler(event, context):
    try:
        s3_bucket_name = "yolo-object-detection-Zihadul" 
        ec2_public_ip = "34.228.24.186"
        
        if isinstance(event, dict) and 'body' in event:
            body = json.loads(event['body'] or '{}')
        else:
            body = event or {}
            
        image_name = body.get('image_name', 'bus.jpg').strip()

        s3_response = s3_client.get_object(Bucket=s3_bucket_name, Key=image_name)
        image_bytes = s3_response['Body'].read()

        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        url = f"http://{ec2_public_ip}:5000/detect"
        
        data = []
        data.append(f'--{boundary}'.encode('utf-8'))
        data.append(f'Content-Disposition: form-data; name="image"; filename="{image_name}"'.encode('utf-8'))
        data.append('Content-Type: image/jpeg'.encode('utf-8'))
        data.append(''.encode('utf-8'))
        data.append(image_bytes)
        data.append(f'--{boundary}--'.encode('utf-8'))
        data.append(''.encode('utf-8'))
        payload = b'\r\n'.join(data)

        req = urllib.request.Request(url, data=payload, method='POST')
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        req.add_header('Content-Length', len(payload))

        with urllib.request.urlopen(req, timeout=45) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            detected_items = res_body.get('objects_found', 'Unknown items')

        image_id = f"IMG_{int(datetime.utcnow().timestamp())}"
        timestamp_str = datetime.utcnow().isoformat()
        
        result_payload = {
            "image_id": image_id,
            "file_processed": image_name,
            "objects_found": detected_items,
            "timestamp": timestamp_str
        }

        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=f"results/{image_id}_result.json",
            Body=json.dumps(result_payload, indent=4),
            ContentType='application/json'
        )

        table.put_item(
            Item={
                'ImageID': image_id,
                'ImageName': image_name,
                'DetectionResults': detected_items,
                'Timestamp': timestamp_str
            }
        )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result_payload)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }