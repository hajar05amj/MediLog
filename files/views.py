from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from reservations.models import Reservation
from tracking.models import TrackingLog
from .models import ResultFile
from rest_framework.parsers import MultiPartParser, FormParser

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, res_id):
        file_obj = request.FILES.get('resultFile')
        if not file_obj:
            return Response({'success': False, 'message': 'Aucun fichier'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            r = Reservation.objects.get(id=res_id)
            rf = ResultFile.objects.create(reservation=r, file=file_obj)
            r.status = 'resultat'
            r.save()
            TrackingLog.objects.create(reservation=r, status='resultat')
            return Response({'success': True, 'fileUrl': rf.file.url})
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
