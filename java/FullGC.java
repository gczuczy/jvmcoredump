import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.ExecutorService;

class TestObject {
    String str;
    TestObject ref;

    public TestObject(String _str, TestObject _to) {
	ref = _to;
	str = _str;
    }
}

public class FullGC {
    static TestObject anchor;

    public static void main(String []args) {
	Runnable r = new Runnable() {
		public void run() {
		    allocate();
		}
	    };

	int size = 2;
	ExecutorService exec = Executors.newFixedThreadPool(size);
	for (int i=0; i<size; ++i) {
	    exec.execute(r);
	}

	while (!exec.isTerminated()) {
	    try {
		Thread.sleep(1);
	    }
	    catch (Exception e) {
	    }
	}
    }

    public static void doGC() {
	boolean failed = false;

	do {
	    failed = false;
	    anchor = null;
	    System.gc();
	    System.runFinalization();
	    try {
		anchor = new TestObject("Fo", null);
	    }
	    catch ( Exception e ) {
		failed = true;
	    }
	} while ( failed );
    }

    public static void allocate() {
	try {
	    TimeUnit.SECONDS.sleep(1);
	}
	catch (Exception e) {
	}
	System.out.println("Allocating memory");

	anchor = new TestObject("Fo", null);
	TestObject to = anchor;
	while ( true ) {
	    try {
		// this has to be sanitized, but will block the
		// progress anyway
		to = new TestObject("Soblity", to);
	    }
	    catch (java.lang.OutOfMemoryError e) {
		System.out.println("OutOfMemoryError");
		doGC();
	    }
	}
    }
    
}
