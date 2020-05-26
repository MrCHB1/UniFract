# UniFract
UniFract is a fractal explorer for Ubuntu 18.04 and above.

## How to use
To use the program, just copy the code, and paste it in the Python IDE. Requires version Python 3 or above.

As long as you don't steal the code, you can use it to run this program.

## Things you can do
What you can do with the code is that you can modify the given formulas!

Just look for something like this:
```
c = pow(c, float(PowerRe)) + c0
```

Once you have found it, you can change it to any formula you want!
You can also use hybrid fractals like the following:
```
c = pow(c, float(PowerRe)) + c0
numIterations += 1

...

c = pow(np.conj(c), float(PowerRe)) + c0
numIterations += 1
```

This example combines both the Mandelbrot and Tricorn fractals.

You can also add in your own fractals by following these steps.

Step 1) Look for the following code
```
...

elif fractalType == "Custom":
  ...
```
Step 2) Go to the top of this function and put in the following code snippet.
```
elif fractalType == "Your Fractal Name Here": # The name of your Fractal
  # Here lies your custom formula
...
```

Step 3) Once that's done, go to the last class of the code, and look for this:
```
FractalTypes = ["Mandelbrot", "Tricorn / Mandelbar", "Burning Ship", ... , "Custom"]
```

Go to the last item in the list, and type EXACTLY what the name of your custom fractal. If you dont do this, then the fractal you provided will not show up.

E.G.
```
FractalTypes = [..., "Your Fractal Name Here", "Custom"]
```

And you are pretty much done! Enjoy your custom fractal!

## Screenshots
![Here are some screenshots from UniFract:](/Pictures/Screenshot from 2020-05-26 08-45-55.png)
