(let empty? (lambda (ls) (= ls 'empty)))
(let len (lambda (ls)
    (if (empty? ls)
        0
        (+ 1 (len (rst ls))))))