title: Making Mathematics Open Source
authors: ['Eyad Loutfi']

![sigplan](sigplan.png)
    
One of the more interesting consequences of interactive theorem proving in recent years has been the realization of its potential both to enhance collaboration among professional mathematicians and bridge the gap of professional mathematics for software engineers and others from less traditional academic backgrounds. 

Many of the benefits of mathematicians adopting such technologies are obvious - digitizing a library of theorems would open it up to search and other automotive tools, which could then be used to assist in the building of more complicated modern proofs. Should we reach the point where modern research level proofs are built with or at least checked by a theorem prover, ensuring correctness would no longer be a matter of faith in the author or in the wait for peer review. 

The technology is still in its infancy in adoption by the larger mathematical community, in part since to get a proof to make sense to a computer requires consideration of many smaller details - often hand waved away or treated more informally in real life. In turn, the technology is ways off from mathematicians feeling it’s easier to work with proof assistants than without, and therefore worth the opportunity cost to learn. That being said, this comes closer to being a reality the more automation there is and the more mathematics gets digitzed. 

Great strides are already being seen - a library called mathlib for the theorem prover Lean has seen over half the standard undergrad math curriculum programmed into it the last few years (as of writing, it contains 116,770 definitions and 236,001 theorems). Several laborious proofs have also been formally verified, and last year, a notoriously difficult problem - the value of the fifth busy beaver number was proven specifically in the rocq theorem prover. Not just that, but it was done by a group that included many non-mathematicians. 

## Background

The busy beaver function is one which gives deep insights into computability, as the nth busy beaver is the maximum number of steps a machine with n rules can take before halting. This means if you know the nth busy beaver and your program runs for longer than that, that program is guaranteed to run forever. At first glance, this might suggest a workaround to the famously uncomputable halting problem, until one learns that this function too is uncomputable. Uncomputable here means that there cannot exist any algorithm that can take any input and spit out the corresponding output, and it shows up constantly in the theory of computation to remind us of the expressive power and limitations of what computers can and can’t do. Therefore, it is not even a given that we’ll always be able to find the next busy beaver number, and the difficulty certainly explodes to a tremendous degree with each value that has been found. 
