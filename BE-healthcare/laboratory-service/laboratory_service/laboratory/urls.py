from django.urls import path
from . import views

urlpatterns = [
    path('l/get-typetest-types', views.get_typetest_types, name='get_typetest_types'),
    path('l/create-typetest', views.create_typetest, name='create_typetest'),
    path('l/get-all-typetest', views.get_all_typetests, name='get_all_typetests'),
    path('l/get-typetest-by-id', views.get_typetest_by_id, name='get_typetest_by_id'),
    path('l/change-active-typetest-by-id', views.change_typetest_active, name='change_typetest_active'),
    path('l/update-typetest', views.update_typetest, name='update_typetest'),
    path('l/create-test-requests', views.create_test_requests, name='create_test_requests'),
    path('l/get-test-requests-by-medical-record', views.get_test_requests_by_medical_record, name='get_test_requests_by_medical_record'),
    path('l/mark-test-requests-paid', views.mark_test_requests_paid, name='mark_test_requests_paid'), 
    path('l/create-test-result', views.create_test_result, name='create_test_result'), 
    path('l/get-annotated-image-test-result-by-test-request', views.get_annotated_image_test_result_by_test_request, name='get_annotated_image_test_result_by_test_request'), 
    # path('l/get-all-annotated-images-by-medical-id', views.get_all_annotated_images_by_medical_id, name='get_all_annotated_images_by_medical_id'), 
    path('l/get-history-test-requests-by-medical', views.get_history_test_requests_by_medical_record, name='get_history_test_requests_by_medical_record'), 

] 