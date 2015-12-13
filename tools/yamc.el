

(defun yamc-post (what)
  (interactive)
  (let ((url-request-method "POST")
		(url-request-data what))
	(with-current-buffer 
		(url-retrieve-synchronously "http://192.168.0.13") 
	  (buffer-string))))

(yamc-post 

(url-http-options "http://192.168.0.13")
