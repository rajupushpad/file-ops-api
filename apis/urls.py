from django.urls import path
from . import views

urlpatterns = [
    path('convert-pdf-to-docx', views.convert_pdf_to_docx, name='convert-file-pdf-to-docx'),
    path('convert-pdf-to-text', views.convert_pdf_to_text_file, name='convert-file-pdf-to-text'),
    path('convert-pdf-to-ppt', views.convert_pdf_to_ppt_file, name='convert-file-pdf-to-ppt'),
    path('convert-pdf-to-excel', views.convert_pdf_to_excel_file, name='convert-file-pdf-to-excel'),
    path('convert-docx-to-pdf', views.convert_docx_to_pdf, name='convert-file-docx-to-pdf'),
    path('merge-pdfs', views.merge_pdfs, name='merge-pdfs'),
    path('convert-image-to-pdf', views.convert_image_to_pdf, name='convert-image-to-pdf'),
    path('convert-pdf-to-image', views.convert_pdf_to_image, name='convert-pdf-to-image'),
    path('convert-jpg-to-png', views.convert_jpg_to_png, name='convert_jpg_to_png'),
    path('convert-png-to-jpg', views.convert_png_to_jpg, name='convert_png_to_jpg'), 
    path('compress-pdf', views.compress_pdf, name='compress_pdf'),
    path('enhance-pdf-quality', views.enhance_pdf_quality, name='enhance_pdf_quality'),

    # path('convert-png-to-svg', views.convert_png_to_svg, name='convert_png_to_svg'), // todo  
    # path('convert-svg-to-png', views.convert_svg_to_png, name='convert_svg_to_png'), 
    path('compress-image', views.compress_image, name='compress_image'),
]